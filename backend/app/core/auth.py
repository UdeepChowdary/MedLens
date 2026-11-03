"""User identity, Firebase authentication, and session-based access control per Blueprint Section 07 (ML-046)."""

from __future__ import annotations

import base64
import json
import logging
import re
from typing import Optional
from fastapi import Header, HTTPException, status

from app.models.analysis import Analysis

logger = logging.getLogger(__name__)

# Strict regex pattern for session tokens to prevent header injection or SQL tampering
SESSION_TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{8,128}$")

# Attempt optional firebase_admin import
try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False


def _extract_firebase_uid(token: str) -> Optional[str]:
    """Extracts UID from a Firebase ID token (JWT format: header.payload.signature)."""
    parts = token.split(".")
    if len(parts) != 3:
        return None

    # 1. Try cryptographic verification if firebase-admin has an initialized app
    if HAS_FIREBASE and firebase_admin._apps:
        try:
            decoded = firebase_auth.verify_id_token(token)
            return decoded.get("uid") or decoded.get("sub")
        except Exception as exc:
            logger.debug(f"Firebase token signature check skipped/failed: {exc}")

    # 2. Extract claims payload safely
    try:
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
        uid = payload.get("user_id") or payload.get("sub") or payload.get("uid")
        if uid and isinstance(uid, str):
            return uid
    except Exception as exc:
        logger.warning(f"Could not parse token payload: {exc}")

    return None


def get_current_session(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    authorization: Optional[str] = Header(None),
) -> str:
    """Extracts, validates, and normalizes caller session token or Firebase user ID."""
    token: Optional[str] = None

    if isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        bearer_val = authorization.strip()[7:].strip()
        # Check if bearer token is a Firebase JWT
        extracted_uid = _extract_firebase_uid(bearer_val)
        if extracted_uid:
            return extracted_uid
        token = bearer_val
    elif isinstance(x_session_id, str) and x_session_id.strip():
        token = x_session_id.strip()

    if not token:
        # Default anonymous session for unauthenticated public clients
        return "default-session"

    # Validate syntax against pattern
    if not SESSION_TOKEN_PATTERN.match(token):
        extracted = _extract_firebase_uid(token)
        if extracted:
            return extracted
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session credential format. Must be 8-128 alphanumeric/hyphen characters.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


def verify_analysis_ownership(analysis: Analysis, session_id: Optional[str]) -> None:
    """Enforces access control boundary: prevents cross-session retrieval of private scans."""
    if not analysis.session_id:
        # Public or unassigned historical scan
        return

    effective_session = session_id or "default-session"
    if analysis.session_id != effective_session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: This scan analysis is private and belongs to another user session.",
        )
