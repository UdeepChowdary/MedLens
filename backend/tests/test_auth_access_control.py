"""Tests for User Identity, Session Authentication, and Access Control (ML-046)."""

import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.core.auth import get_current_session, verify_analysis_ownership
from app.models.analysis import Analysis


def create_test_image_bytes() -> bytes:
    """Creates a minimal valid RGB PNG for test uploads."""
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============================================================================
# 1. Unit Tests for Session Token Parsing and Security Validation
# ============================================================================

def test_session_token_validation_success():
    """Verifies that valid alphanumeric and hyphenated session tokens are accepted."""
    valid_tokens = [
        "session-12345678",
        "sess_9876543210abcdef",
        "user-session.v1.alpha",
        "12345678-abcd-ef01-2345-6789abcdef01",
    ]
    for token in valid_tokens:
        extracted = get_current_session(x_session_id=token)
        assert extracted == token

    # Test Bearer header format
    bearer_extracted = get_current_session(authorization="Bearer valid-token-123456")
    assert bearer_extracted == "valid-token-123456"

    # Test default fallback when no credentials provided
    assert get_current_session() == "default-session"


def test_session_token_validation_rejection():
    """Verifies that malformed, too short, or injection-like tokens trigger HTTP 401."""
    malformed_tokens = [
        "short",  # < 8 chars
        "session with spaces 123",
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "token; DROP TABLE analyses;--",
        "x" * 150,  # > 128 chars
    ]
    for bad_token in malformed_tokens:
        with pytest.raises(HTTPException) as exc_info:
            get_current_session(x_session_id=bad_token)
        assert exc_info.value.status_code == 401


# ============================================================================
# 2. Integration Tests for Session Ownership and Cross-Session Isolation
# ============================================================================

def test_analysis_creation_tagged_with_session(client: TestClient):
    """Verifies that creating an analysis tags the record with the caller's session ID."""
    session_id = "session-test-creator-001"
    image_bytes = create_test_image_bytes()

    res = client.post(
        "/api/v1/analyses",
        files={"file": ("test_label.png", image_bytes, "image/png")},
        headers={"X-Session-ID": session_id},
    )
    assert res.status_code == 202
    analysis_id = res.json()["analysis_id"]

    # Verify that creator can retrieve the record
    get_res = client.get(
        f"/api/v1/analyses/{analysis_id}",
        headers={"X-Session-ID": session_id},
    )
    assert get_res.status_code == 200
    assert get_res.json()["analysis_id"] == analysis_id


def test_session_history_isolation(client: TestClient):
    """Verifies that list_analyses isolates records strictly between sessions."""
    sess_a = "session-user-a-11111"
    sess_b = "session-user-b-22222"
    image_bytes = create_test_image_bytes()

    # User A creates a scan
    res_a = client.post(
        "/api/v1/analyses",
        files={"file": ("label_a.png", image_bytes, "image/png")},
        headers={"X-Session-ID": sess_a},
    )
    id_a = res_a.json()["analysis_id"]

    # User B creates a scan
    res_b = client.post(
        "/api/v1/analyses",
        files={"file": ("label_b.png", image_bytes, "image/png")},
        headers={"X-Session-ID": sess_b},
    )
    id_b = res_b.json()["analysis_id"]

    # Query history as User A
    list_a = client.get("/api/v1/analyses", headers={"X-Session-ID": sess_a}).json()
    ids_seen_by_a = {item["analysis_id"] for item in list_a}
    assert id_a in ids_seen_by_a, "User A should see their own scan"
    assert id_b not in ids_seen_by_a, "User A must NOT see User B's scan"

    # Query history as User B
    list_b = client.get("/api/v1/analyses", headers={"X-Session-ID": sess_b}).json()
    ids_seen_by_b = {item["analysis_id"] for item in list_b}
    assert id_b in ids_seen_by_b, "User B should see their own scan"
    assert id_a not in ids_seen_by_b, "User B must NOT see User A's scan"


def test_cross_session_retrieval_forbidden(client: TestClient):
    """Verifies that User B receives HTTP 403 Forbidden when attempting to access User A's private scan."""
    sess_owner = "session-owner-alpha-99"
    sess_intruder = "session-intruder-beta-88"
    image_bytes = create_test_image_bytes()

    # Owner creates scan
    create_res = client.post(
        "/api/v1/analyses",
        files={"file": ("owner_label.png", image_bytes, "image/png")},
        headers={"X-Session-ID": sess_owner},
    )
    scan_id = create_res.json()["analysis_id"]

    # Intruder attempts to fetch owner's scan
    intruder_res = client.get(
        f"/api/v1/analyses/{scan_id}",
        headers={"X-Session-ID": sess_intruder},
    )
    assert intruder_res.status_code == 403
    assert "Access denied" in intruder_res.json()["detail"]

    # Unauthenticated client (default-session) also blocked
    anon_res = client.get(f"/api/v1/analyses/{scan_id}")
    assert anon_res.status_code == 403

    # Legitimate owner can access successfully
    owner_res = client.get(
        f"/api/v1/analyses/{scan_id}",
        headers={"X-Session-ID": sess_owner},
    )
    assert owner_res.status_code == 200
    assert owner_res.json()["analysis_id"] == scan_id


def test_legacy_public_scan_backward_compatibility(client: TestClient):
    """Verifies that demo-scan or unassigned legacy scans remain accessible without 403."""
    res_default = client.get("/api/v1/analyses/demo-scan")
    assert res_default.status_code == 200

    res_custom = client.get(
        "/api/v1/analyses/demo-scan",
        headers={"X-Session-ID": "session-any-user-777"},
    )
    assert res_custom.status_code == 200


def test_malformed_session_header_endpoint_rejection(client: TestClient):
    """Verifies that endpoints reject injection or illegal session IDs with HTTP 401."""
    res = client.get(
        "/api/v1/analyses",
        headers={"X-Session-ID": "' OR 1=1 --"},
    )
    assert res.status_code == 401
    assert "Invalid session credential format" in res.json()["detail"]

