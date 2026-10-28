"""Unit and integration tests for external reference adapters, cache, and coordinator."""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.schemas.product import EvidenceSourceSchema
from app.services.references.base import BaseReferenceAdapter, ReferenceData
from app.services.references.cache import ReferenceCache
from app.services.references.coordinator import ReferenceCoordinator
from app.services.references.indian_adapter import IndianReferenceAdapter
from app.services.references.openfda_adapter import OpenFDAAdapter
from app.services.references.pubchem_adapter import PubChemAdapter


@pytest.mark.asyncio
async def test_reference_cache_set_and_get(db_session):
    """Verifies that ReferenceCache accurately serializes, stores, and retrieves ReferenceData."""
    cache = ReferenceCache(session=db_session)
    sample_data = ReferenceData(
        source_name="openFDA Drug Product Labels",
        source_url="https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=paracetamol",
        source_id="FDA-PARACETAMOL",
        jurisdiction="US",
        canonical_name="Paracetamol",
        indications=["Fever and mild pain relief."],
        warnings=["Liver warning with excessive dose."],
    )

    await cache.set("openfda", "paracetamol", sample_data, ttl_days=7)

    retrieved = await cache.get("openfda", "paracetamol")
    assert retrieved is not None
    assert retrieved.canonical_name == "Paracetamol"
    assert retrieved.source_id == "FDA-PARACETAMOL"
    assert len(retrieved.warnings) == 1
    assert "Liver warning" in retrieved.warnings[0]


@pytest.mark.asyncio
async def test_reference_cache_expiration(db_session):
    """Verifies that expired entries return None and are purged."""
    cache = ReferenceCache(session=db_session)
    sample_data = ReferenceData(
        source_name="PubChem",
        source_url="https://pubchem.ncbi.nlm.nih.gov/compound/1983",
        source_id="CID-1983",
        jurisdiction="GLOBAL",
        canonical_name="Paracetamol",
    )

    # Set with negative TTL so it is already expired
    await cache.set("pubchem", "paracetamol", sample_data, ttl_days=-1)

    retrieved = await cache.get("pubchem", "paracetamol")
    assert retrieved is None


@pytest.mark.asyncio
async def test_reference_cache_invalidation(db_session):
    """Verifies that explicit cache invalidation purges the row."""
    cache = ReferenceCache(session=db_session)
    sample_data = ReferenceData(
        source_name="Indian Pharmacopoeia",
        source_url="https://ipc.gov.in/",
        source_id="IPC-001",
        jurisdiction="IN",
        canonical_name="Metformin",
    )

    await cache.set("indian", "metformin", sample_data, ttl_days=7)
    assert await cache.get("indian", "metformin") is not None

    invalidated = await cache.invalidate("indian", "metformin")
    assert invalidated is True
    assert await cache.get("indian", "metformin") is None


@pytest.mark.asyncio
async def test_openfda_adapter_parsing():
    """Verifies openFDA JSON parsing of indications, boxed warnings, and precautions."""
    mock_response_data = {
        "results": [
            {
                "id": "label-abc-123",
                "openfda": {
                    "substance_name": ["ACETAMINOPHEN"],
                    "dosage_form": ["TABLET"],
                },
                "purpose": ["Pain reliever / Fever reducer."],
                "boxed_warning": ["LIVER WARNING: This product contains acetaminophen. Severe liver damage may occur."],
                "warnings": ["Allergy alert: Acetaminophen may cause severe skin reactions."],
                "contraindications": ["Do not use with any other drug containing acetaminophen."],
                "adverse_reactions": ["Nausea, rash, hypersensitivity."],
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data
    mock_resp.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_resp

    adapter = OpenFDAAdapter(client=mock_client)
    result = await adapter.lookup("Paracetamol")

    assert result is not None
    assert result.source_name == "openFDA Drug Product Labels"
    assert result.jurisdiction == "US"
    assert len(result.indications) > 0
    assert any("Pain reliever" in ind for ind in result.indications)
    assert len(result.warnings) > 0
    assert any("LIVER WARNING" in w for w in result.warnings)
    assert len(result.contraindications) > 0


@pytest.mark.asyncio
async def test_openfda_adapter_404_resilience():
    """Verifies openFDA 404 response returns None without crashing."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 404
    mock_client.get.return_value = mock_resp

    adapter = OpenFDAAdapter(client=mock_client)
    result = await adapter.lookup("NonexistentSubstance12345")
    assert result is None


@pytest.mark.asyncio
async def test_openfda_adapter_network_error_resilience():
    """Verifies openFDA network errors return None gracefully."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ConnectTimeout("Connection timed out")

    adapter = OpenFDAAdapter(client=mock_client)
    result = await adapter.lookup("Amoxicillin")
    assert result is None


@pytest.mark.asyncio
async def test_pubchem_adapter_parsing():
    """Verifies PubChem PUG REST parsing for CID, SMILES, and molecular formula."""
    mock_response_data = {
        "PropertyTable": {
            "Properties": [
                {
                    "CID": 1983,
                    "MolecularFormula": "C8H9NO2",
                    "MolecularWeight": "151.16",
                    "CanonicalSMILES": "CC(=O)NC1=CC=C(C=C1)O",
                    "IUPACName": "N-(4-hydroxyphenyl)acetamide",
                }
            ]
        }
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data
    mock_resp.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_resp

    adapter = PubChemAdapter(client=mock_client)
    result = await adapter.lookup("Paracetamol")

    assert result is not None
    assert result.source_name == "National Library of Medicine / PubChem"
    assert result.jurisdiction == "GLOBAL"
    assert result.chemical_identifier == "CID:1983"
    assert result.molecular_formula == "C8H9NO2"
    assert result.smiles == "CC(=O)NC1=CC=C(C=C1)O"
    assert "https://pubchem.ncbi.nlm.nih.gov/compound/1983" in result.source_url


@pytest.mark.asyncio
async def test_pubchem_adapter_404_resilience():
    """Verifies PubChem compound not found returns None."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 404
    mock_client.get.return_value = mock_resp

    adapter = PubChemAdapter(client=mock_client)
    result = await adapter.lookup("UnidentifiedCompoundXYZ")
    assert result is None


@pytest.mark.asyncio
async def test_indian_reference_adapter_exact_lookup():
    """Verifies Indian Pharmacopoeia exact lookup for Amoxicillin with Schedule H1 statutory warning."""
    adapter = IndianReferenceAdapter()
    result = await adapter.lookup("Amoxicillin")

    assert result is not None
    assert result.source_name == "Indian Pharmacopoeia Commission (IPC) / CDSCO"
    assert result.jurisdiction == "IN"
    assert result.canonical_name == "Amoxicillin"
    assert any("SCHEDULE H1" in w for w in result.warnings)
    assert any("PMBJP" in ind for ind in result.indications)


@pytest.mark.asyncio
async def test_indian_reference_adapter_heuristic_fallback():
    """Verifies fallback statutory classification for unknown Indian medicines with antibiotic suffixes."""
    adapter = IndianReferenceAdapter()
    result = await adapter.lookup("piperacillin")

    assert result is not None
    assert result.jurisdiction == "IN"
    assert result.canonical_name == "Piperacillin"
    assert any("SCHEDULE H1" in w for w in result.warnings)


@pytest.mark.asyncio
async def test_reference_coordinator_aggregation(db_session):
    """Verifies that ReferenceCoordinator executes concurrent adapter queries, caches data, and consolidates profiles."""
    cache = ReferenceCache(session=db_session)

    # Mock openFDA
    mock_fda = AsyncMock(spec=BaseReferenceAdapter)
    mock_fda.name = "openFDA"
    mock_fda.jurisdiction = "US"
    mock_fda.lookup.return_value = ReferenceData(
        source_name="openFDA Drug Product Labels",
        source_url="https://dailymed.nlm.nih.gov/search?q=ibuprofen",
        source_id="FDA-IBU-001",
        jurisdiction="US",
        canonical_name="Ibuprofen",
        indications=["Anti-inflammatory and analgesic."],
        warnings=["Risk of gastrointestinal ulceration."],
    )

    # Mock PubChem
    mock_pubchem = AsyncMock(spec=BaseReferenceAdapter)
    mock_pubchem.name = "PubChem"
    mock_pubchem.jurisdiction = "GLOBAL"
    mock_pubchem.lookup.return_value = ReferenceData(
        source_name="National Library of Medicine / PubChem",
        source_url="https://pubchem.ncbi.nlm.nih.gov/compound/3672",
        source_id="CID-3672",
        jurisdiction="GLOBAL",
        canonical_name="Ibuprofen",
        chemical_identifier="CID:3672",
        smiles="CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        molecular_formula="C13H18O2",
    )

    indian_adapter = IndianReferenceAdapter()

    coordinator = ReferenceCoordinator(
        adapters=[indian_adapter, mock_fda, mock_pubchem],
        cache=cache,
    )

    lookups = await coordinator.lookup_ingredient("Ibuprofen", use_cache=True)

    assert "Indian Pharmacopoeia & CDSCO" in lookups
    assert "openFDA" in lookups
    assert "PubChem" in lookups

    # Verify provenance sources
    evidence_sources = coordinator.build_evidence_sources(lookups)
    assert len(evidence_sources) == 3
    jurisdictions = {s.jurisdiction for s in evidence_sources}
    assert jurisdictions == {"IN", "US", "GLOBAL"}

    # Verify consolidated profile
    consolidated = coordinator.consolidate_clinical_profile(lookups)
    assert consolidated["chemical_identifier"] == "CID:3672"
    assert consolidated["smiles"] == "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    assert consolidated["molecular_formula"] == "C13H18O2"
    assert any("ulceration" in w for w in consolidated["warnings"])
    assert any("SCHEDULE H" in w for w in consolidated["warnings"])

    # Second call should hit the cache
    lookups_cached = await coordinator.lookup_ingredient("Ibuprofen", use_cache=True)
    assert lookups_cached["openFDA"] is not None
    assert lookups_cached["openFDA"].source_id == "FDA-IBU-001"
    # mock_fda.lookup was called only once because cache served the second call
    assert mock_fda.lookup.call_count == 1


@pytest.mark.asyncio
async def test_reference_coordinator_error_tolerance(db_session):
    """Verifies that an unhandled crash in one adapter does not fail the overall aggregation."""
    failing_adapter = AsyncMock(spec=BaseReferenceAdapter)
    failing_adapter.name = "CrashingAdapter"
    failing_adapter.lookup.side_effect = RuntimeError("Fatal crash in network layer")

    indian_adapter = IndianReferenceAdapter()

    coordinator = ReferenceCoordinator(
        adapters=[indian_adapter, failing_adapter],
        cache=ReferenceCache(session=db_session),
    )

    lookups = await coordinator.lookup_ingredient("Paracetamol", use_cache=False)
    assert lookups["CrashingAdapter"] is None
    assert lookups["Indian Pharmacopoeia & CDSCO"] is not None

