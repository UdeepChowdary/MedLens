"""Tests for domain error handling and structured error responses."""

from fastapi.testclient import TestClient


def test_404_error_structure(client: TestClient) -> None:
    """Verifies that AnalysisNotFoundError returns structured JSON error contract."""
    response = client.get("/api/v1/analyses/non-existent-uuid-1234")
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "ERR_ANALYSIS_NOT_FOUND"
    assert "message" in data
    assert "non-existent-uuid-1234" in data["message"]
    assert "timestamp" in data


def test_upload_rejects_unsupported_format(client: TestClient) -> None:
    """Verifies that uploading a non-image file is rejected with 400 and structured error."""
    response = client.post(
        "/api/v1/analyses",
        files={"file": ("test.txt", b"plain text content", "text/plain")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "ERR_IMAGE_VALIDATION_FAILED"
    assert "Unsupported file format" in data["message"]


def test_valid_image_upload_accepted(client: TestClient) -> None:
    """Verifies that well-formed image payload returns 202 Accepted with analysis ID."""
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    response = client.post(
        "/api/v1/analyses",
        files={"file": ("label.png", fake_png, "image/png")},
    )
    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "received"
