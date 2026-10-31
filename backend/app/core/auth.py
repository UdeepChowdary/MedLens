"""User identity and session-based access control per Blueprint Section 07 (ML-046)."""

from __future__ import annotations

import re
from typing import Optional
from fastapi import Header, HTTPException, status

from app.models.analysis import Analysis

# Strict regex pattern for session tokens to prevent header injection or SQL tampering
SESSION_TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{8,128}$")


def get_current_session(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    authorization: Optional[str] = Header(None),
) -> str:
    """Extracts, validates, and normalizes the caller's session token.

    Never trusts client-supplied user IDs directly without session credential validation.
    """
    token: Optional[str] = None

    if isinstance(x_session_id, str) and x_session_id.strip():
        token = x_session_id.strip()
    elif isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        token = authorization.strip()[7:].strip()

    if not token:
        # Default anonymous session for unauthenticated public clients
        return "default-session"

    # Validate syntax against strict pattern
    if not SESSION_TOKEN_PATTERN.match(token):
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

