"""Tests for products catalog and comparison endpoints connected to database."""

from fastapi.testclient import TestClient


def test_search_products_by_brand(client: TestClient) -> None:
    """Verifies searching products by brand name returns valid matches."""
    response = client.get("/api/v1/products/search?q=dolo")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["detected_name"] == "Dolo 650"
    assert data[0]["dosage_form"] == "Tablet"
    assert data[0]["is_verified"] is True


def test_search_products_by_ingredient(client: TestClient) -> None:
    """Verifies searching by active ingredient returns all containing products."""
    response = client.get("/api/v1/products/search?q=paracetamol")
    assert response.status_code == 200
    data = response.json()
    names = [p["detected_name"] for p in data]
    assert "Dolo 650" in names
    assert "Calpol 500" in names


def test_get_product_by_id(client: TestClient) -> None:
    """Verifies fetching specific product by ID."""
    response = client.get("/api/v1/products/dolo-650")
    assert response.status_code == 200
    data = response.json()
    assert data["detected_name"] == "Dolo 650"
    assert data["manufacturer"] == "Micro Labs Ltd"


def test_get_nonexistent_product_returns_404(client: TestClient) -> None:
    """Verifies requesting non-existent product returns standard 404 envelope."""
    response = client.get("/api/v1/products/nonexistent-medicine-xyz")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "ERR_PRODUCT_NOT_FOUND"


def test_compare_products_dolo_vs_calpol(client: TestClient) -> None:
    """Verifies comparing Dolo 650 and Calpol 500 calculates strength delta and ingredient match."""
    response = client.post(
        "/api/v1/comparisons",
        json={"product_id_a": "dolo-650", "product_id_b": "calpol-500"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["comparison_status"] == "partially_comparable"
    assert data["medicine_a"]["name"] == "Dolo 650"
    assert data["medicine_b"]["name"] == "Calpol 500"

    # Active ingredients match
    active_attr = next(a for a in data["attributes"] if a["field"] == "active_ingredients")
    assert active_attr["result"] == "match"

    # Strength difference
    strength_attr = next(a for a in data["attributes"] if a["field"] == "strength")
    assert strength_attr["result"] == "difference"
    assert data["strength_delta"]["difference_detected"] is True
    assert data["strength_delta"]["numeric_delta"] == 150.0
    assert data["strength_delta"]["unit"] == "mg"
    assert "150mg higher active Paracetamol" in data["strength_delta"]["warning"] or "150" in data["strength_delta"]["warning"]

    # Dosage form match
    form_attr = next(a for a in data["attributes"] if a["field"] == "dosage_form")
    assert form_attr["result"] == "match"

    # Bioequivalence disclaimer
    assert data["therapeutic_equivalence"]["status"] == "not_established"


def test_compare_nonexistent_product_returns_404(client: TestClient) -> None:
    """Verifies comparison with invalid product returns 404 error."""
    response = client.post(
        "/api/v1/comparisons",
        json={"product_id_a": "dolo-650", "product_id_b": "phantom-drug-999"},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "ERR_PRODUCT_NOT_FOUND"
