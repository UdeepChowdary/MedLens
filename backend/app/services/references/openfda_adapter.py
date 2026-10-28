"""openFDA Drug Product Label API client adapter."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.services.references.base import BaseReferenceAdapter, ReferenceData

logger = logging.getLogger(__name__)


class OpenFDAAdapter(BaseReferenceAdapter):
    """Retrieves FDA-approved product labels, boxed warnings, and indications."""

    BASE_URL = "https://api.fda.gov/drug/label.json"

    def __init__(self, client: Optional[httpx.AsyncClient] = None, timeout: float = 5.0):
        self._client = client
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "openFDA"

    @property
    def jurisdiction(self) -> str:
        return "US"

    async def lookup(self, drug_name: str) -> Optional[ReferenceData]:
        """Queries openFDA for clinical drug labels by substance or generic name."""
        clean_name = drug_name.strip()
        if not clean_name:
            return None

        queries = [
            f'openfda.substance_name:"{clean_name}"',
            f'openfda.generic_name:"{clean_name}"',
            f'openfda.brand_name:"{clean_name}"',
        ]

        for query in queries:
            try:
                data = await self._fetch(query)
                if data and "results" in data and data["results"]:
                    return self._parse_label(clean_name, data["results"][0])
            except Exception as exc:
                logger.warning("openFDA query failed for query %s: %s", query, exc)
                return None

        return None

    async def _fetch(self, query: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}?search={quote(query)}&limit=1"

        if self._client:
            resp = await self._client.get(url, timeout=self._timeout)
        else:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url)

        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def _parse_label(self, drug_name: str, label_data: Dict[str, Any]) -> ReferenceData:
        openfda_block = label_data.get("openfda", {})
        source_id = label_data.get("id") or label_data.get("set_id") or f"FDA-{drug_name.upper()}"

        # Clean indications
        raw_indications = label_data.get("indications_and_usage") or label_data.get("purpose") or []
        indications = self._extract_clean_text_items(raw_indications, limit=3)

        # Clean boxed warnings & precautions
        boxed = label_data.get("boxed_warning") or []
        warnings_raw = label_data.get("warnings") or label_data.get("warnings_and_cautions") or []
        warnings = self._extract_clean_text_items(boxed + warnings_raw, limit=4)

        # Clean contraindications
        contraindications_raw = label_data.get("contraindications") or []
        contraindications = self._extract_clean_text_items(contraindications_raw, limit=3)

        # Clean adverse reactions
        adverse_raw = label_data.get("adverse_reactions") or []
        adverse_reactions = self._extract_clean_text_items(adverse_raw, limit=3)

        canonical_substances = openfda_block.get("substance_name") or [drug_name.title()]
        canonical_name = canonical_substances[0].title()

        source_url = f"https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={quote(canonical_name)}"

        return ReferenceData(
            source_name="openFDA Drug Product Labels",
            source_url=source_url,
            source_id=str(source_id),
            jurisdiction=self.jurisdiction,
            canonical_name=canonical_name,
            indications=indications,
            contraindications=contraindications,
            warnings=warnings,
            adverse_reactions=adverse_reactions,
            raw_payload={
                "id": source_id,
                "substance_name": canonical_substances,
                "dosage_form": openfda_block.get("dosage_form", []),
            },
        )

    @staticmethod
    def _extract_clean_text_items(raw_items: List[str], limit: int = 3) -> List[str]:
        cleaned: List[str] = []
        for item in raw_items:
            # Strip excessive boilerplate, split sentences if needed
            sentences = [s.strip() for s in item.replace("\n", " ").split(". ") if len(s.strip()) > 10]
            for s in sentences:
                clean_s = s if s.endswith(".") else f"{s}."
                if clean_s not in cleaned:
                    cleaned.append(clean_s)
                if len(cleaned) >= limit:
                    return cleaned
        return cleaned
