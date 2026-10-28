"""Reference coordinator orchestrating multi-provider lookups, caching, and provenance."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from app.schemas.product import EvidenceSourceSchema
from app.services.references.base import BaseReferenceAdapter, ReferenceData
from app.services.references.cache import ReferenceCache
from app.services.references.indian_adapter import IndianReferenceAdapter
from app.services.references.openfda_adapter import OpenFDAAdapter
from app.services.references.pubchem_adapter import PubChemAdapter

logger = logging.getLogger(__name__)


class ReferenceCoordinator:
    """Coordinates queries across external regulatory, pharmacopeial, and chemical sources."""

    def __init__(
        self,
        adapters: Optional[List[BaseReferenceAdapter]] = None,
        cache: Optional[ReferenceCache] = None,
    ):
        self.adapters = adapters or [
            IndianReferenceAdapter(),
            OpenFDAAdapter(),
            PubChemAdapter(),
        ]
        self.cache = cache or ReferenceCache()

    async def lookup_ingredient(
        self,
        drug_name: str,
        use_cache: bool = True,
    ) -> Dict[str, Optional[ReferenceData]]:
        """Queries all adapters concurrently with cache fallback.

        Returns a dictionary mapping adapter name to its ReferenceData (or None if unavailable).
        """
        clean_name = drug_name.strip()
        if not clean_name:
            return {}

        tasks = [
            self._query_single_adapter(adapter, clean_name, use_cache=use_cache)
            for adapter in self.adapters
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged: Dict[str, Optional[ReferenceData]] = {}
        for adapter, res in zip(self.adapters, results):
            if isinstance(res, Exception):
                logger.warning("Adapter %s raised exception for %s: %s", adapter.name, clean_name, res)
                merged[adapter.name] = None
            else:
                merged[adapter.name] = res

        return merged

    async def _query_single_adapter(
        self,
        adapter: BaseReferenceAdapter,
        drug_name: str,
        use_cache: bool,
    ) -> Optional[ReferenceData]:
        # 1. Check persistent SQLite cache
        if use_cache and self.cache:
            try:
                cached = await self.cache.get(adapter.name, drug_name)
                if cached:
                    return cached
            except Exception as exc:
                logger.warning("Cache read failed for %s:%s: %s", adapter.name, drug_name, exc)

        # 2. Live remote lookup
        try:
            data = await adapter.lookup(drug_name)
        except Exception as exc:
            logger.warning("Adapter %s execution failed: %s", adapter.name, exc)
            return None

        # 3. Store into cache if successful
        if data and use_cache and self.cache:
            try:
                await self.cache.set(adapter.name, drug_name, data, ttl_days=7)
            except Exception as exc:
                logger.warning("Cache write failed for %s:%s: %s", adapter.name, drug_name, exc)

        return data

    def build_evidence_sources(
        self,
        lookup_results: Dict[str, Optional[ReferenceData]],
    ) -> List[EvidenceSourceSchema]:
        """Builds traceable EvidenceSourceSchema objects from all responding reference providers."""
        sources: List[EvidenceSourceSchema] = []
        seen_urls = set()

        for data in lookup_results.values():
            if data and data.source_url not in seen_urls:
                seen_urls.add(data.source_url)
                sources.append(
                    EvidenceSourceSchema(
                        name=data.source_name,
                        url=data.source_url,
                        source_id=data.source_id,
                        jurisdiction=data.jurisdiction,
                        retrieval_date=data.retrieved_at,
                    )
                )

        return sources

    def consolidate_clinical_profile(
        self,
        lookup_results: Dict[str, Optional[ReferenceData]],
    ) -> Dict[str, Any]:
        """Consolidates clinical indications, contraindications, and warnings across jurisdictions."""
        indications: List[str] = []
        contraindications: List[str] = []
        warnings: List[str] = []
        adverse_reactions: List[str] = []

        chemical_identifier: Optional[str] = None
        smiles: Optional[str] = None
        molecular_formula: Optional[str] = None

        for data in lookup_results.values():
            if not data:
                continue

            for ind in data.indications:
                if ind not in indications:
                    indications.append(ind)

            for contra in data.contraindications:
                if contra not in contraindications:
                    contraindications.append(contra)

            for warn in data.warnings:
                if warn not in warnings:
                    warnings.append(warn)

            for adv in data.adverse_reactions:
                if adv not in adverse_reactions:
                    adverse_reactions.append(adv)

            if data.chemical_identifier and not chemical_identifier:
                chemical_identifier = data.chemical_identifier
            if data.smiles and not smiles:
                smiles = data.smiles
            if data.molecular_formula and not molecular_formula:
                molecular_formula = data.molecular_formula

        return {
            "indications": indications,
            "contraindications": contraindications,
            "warnings": warnings,
            "adverse_reactions": adverse_reactions,
            "chemical_identifier": chemical_identifier,
            "smiles": smiles,
            "molecular_formula": molecular_formula,
        }
