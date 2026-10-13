"""Tests for health probe and openapi endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Verifies that GET /api/v1/health returns 200 OK and valid status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_openapi_available(client: TestClient) -> None:
    """Verifies that OpenAPI documentation schema is registered."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/analyses" in schema["paths"]
    assert "/api/v1/products/search" in schema["paths"]
    assert "/api/v1/comparisons" in schema["paths"]
