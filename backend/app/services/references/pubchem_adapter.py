"""PubChem Compound API adapter using PUG REST interface."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from urllib.parse import quote

import httpx

from app.services.references.base import BaseReferenceAdapter, ReferenceData

logger = logging.getLogger(__name__)


class PubChemAdapter(BaseReferenceAdapter):
    """Retrieves chemical structure, SMILES, CID, and formula from NCBI PubChem."""

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"

    def __init__(self, client: Optional[httpx.AsyncClient] = None, timeout: float = 5.0):
        self._client = client
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "PubChem"

    @property
    def jurisdiction(self) -> str:
        return "GLOBAL"

    async def lookup(self, drug_name: str) -> Optional[ReferenceData]:
        """Queries PubChem PUG REST API for compound chemical identity and notation."""
        clean_name = drug_name.strip()
        if not clean_name:
            return None

        url = f"{self.BASE_URL}/{quote(clean_name)}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"

        try:
            if self._client:
                resp = await self._client.get(url, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    resp = await client.get(url)

            if resp.status_code == 404:
                logger.info("PubChem returned 404 for compound: %s", clean_name)
                return None

            resp.raise_for_status()
            data = resp.json()
            return self._parse_compound(clean_name, data)

        except Exception as exc:
            logger.warning("PubChem query failed for %s: %s", clean_name, exc)
            return None

    def _parse_compound(self, drug_name: str, payload: Dict[str, Any]) -> Optional[ReferenceData]:
        properties = (
            payload.get("PropertyTable", {})
            .get("Properties", [])
        )
        if not properties:
            return None

        first = properties[0]
        cid = first.get("CID")
        formula = first.get("MolecularFormula")
        smiles = first.get("CanonicalSMILES")
        iupac = first.get("IUPACName")

        source_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}" if cid else "https://pubchem.ncbi.nlm.nih.gov/"
        source_id = f"CID-{cid}" if cid else f"PUBCHEM-{drug_name.upper()}"

        indications = []
        if iupac:
            indications.append(f"Standard chemical identifier: {iupac}.")

        return ReferenceData(
            source_name="National Library of Medicine / PubChem",
            source_url=source_url,
            source_id=source_id,
            jurisdiction=self.jurisdiction,
            canonical_name=drug_name.title(),
            chemical_identifier=f"CID:{cid}" if cid else None,
            smiles=smiles,
            molecular_formula=formula,
            indications=indications,
            contraindications=[],
            warnings=[],
            adverse_reactions=[],
            raw_payload={
                "CID": cid,
                "MolecularFormula": formula,
                "MolecularWeight": first.get("MolecularWeight"),
                "CanonicalSMILES": smiles,
                "IUPACName": iupac,
            },
        )
