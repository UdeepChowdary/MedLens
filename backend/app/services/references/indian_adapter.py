"""Indian Pharmacopoeia, CDSCO regulatory schedules, and Jan Aushadhi adapter."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.services.references.base import BaseReferenceAdapter, ReferenceData

logger = logging.getLogger(__name__)

# Curated reference registry for standard Indian pharmacopeial specifications
INDIAN_PHARMACOPOEIA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "paracetamol": {
        "canonical_name": "Paracetamol",
        "ip_monograph": "IP 2022 Monograph, Vol. III, p. 2841",
        "schedule": "OTC / General Sales List",
        "warnings": [
            "Overdose warning: Taking more than daily dose may cause serious liver damage or allergic reactions.",
            "Must not be used concurrently with other paracetamol-containing products.",
        ],
        "contraindications": ["Severe hepatic impairment", "Known paracetamol hypersensitivity"],
        "indications": ["Analgesic and antipyretic for mild-to-moderate pain and pyrexia."],
        "jan_aushadhi_code": "PMBJP-00124",
        "jan_aushadhi_generic_name": "Paracetamol Tablets IP 500mg",
        "approx_jan_aushadhi_price_inr": 10.0,
    },
    "amoxicillin": {
        "canonical_name": "Amoxicillin",
        "ip_monograph": "IP 2022 Monograph, Vol. II, p. 1120",
        "schedule": "Schedule H1",
        "warnings": [
            "SCHEDULE H1 PRESCRIPTION DRUG - CAUTION: It is dangerous to take this preparation except in accordance with the medical advice.",
            "Not to be sold by retail without the prescription of a Registered Medical Practitioner.",
        ],
        "contraindications": ["History of penicillin allergy", "Infectious mononucleosis"],
        "indications": ["Broad-spectrum beta-lactam antibacterial therapy."],
        "jan_aushadhi_code": "PMBJP-00045",
        "jan_aushadhi_generic_name": "Amoxicillin Capsules IP 500mg",
        "approx_jan_aushadhi_price_inr": 35.0,
    },
    "azithromycin": {
        "canonical_name": "Azithromycin",
        "ip_monograph": "IP 2022 Monograph, Vol. II, p. 1290",
        "schedule": "Schedule H1",
        "warnings": [
            "SCHEDULE H1 PRESCRIPTION DRUG - CAUTION: It is dangerous to take this preparation except in accordance with the medical advice.",
            "Not to be sold by retail without the prescription of a Registered Medical Practitioner.",
        ],
        "contraindications": ["Hypersensitivity to macrolide antibiotics", "Hepatic dysfunction"],
        "indications": ["Macrolide antibacterial for respiratory tract and soft tissue infections."],
        "jan_aushadhi_code": "PMBJP-00067",
        "jan_aushadhi_generic_name": "Azithromycin Tablets IP 500mg",
        "approx_jan_aushadhi_price_inr": 55.0,
    },
    "metformin": {
        "canonical_name": "Metformin",
        "ip_monograph": "IP 2022 Monograph, Vol. III, p. 2510",
        "schedule": "Schedule H",
        "warnings": [
            "SCHEDULE H PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
            "Risk of lactic acidosis: Monitor renal function prior to initiation.",
        ],
        "contraindications": ["Severe renal impairment (eGFR < 30 mL/min)", "Acute metabolic acidosis"],
        "indications": ["First-line biguanide oral antihyperglycemic agent for Type 2 diabetes mellitus."],
        "jan_aushadhi_code": "PMBJP-00312",
        "jan_aushadhi_generic_name": "Metformin Hydrochloride Sustained Release Tablets IP 500mg",
        "approx_jan_aushadhi_price_inr": 12.0,
    },
    "atorvastatin": {
        "canonical_name": "Atorvastatin",
        "ip_monograph": "IP 2022 Monograph, Vol. II, p. 1260",
        "schedule": "Schedule H",
        "warnings": [
            "SCHEDULE H PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
            "Myopathy warning: Report unexplained muscle pain, tenderness, or weakness immediately.",
        ],
        "contraindications": ["Active liver disease", "Pregnancy and lactation"],
        "indications": ["HMG-CoA reductase inhibitor for hypercholesterolemia and cardiovascular risk reduction."],
        "jan_aushadhi_code": "PMBJP-00105",
        "jan_aushadhi_generic_name": "Atorvastatin Tablets IP 10mg",
        "approx_jan_aushadhi_price_inr": 18.0,
    },
    "pantoprazole": {
        "canonical_name": "Pantoprazole",
        "ip_monograph": "IP 2022 Monograph, Vol. III, p. 2825",
        "schedule": "Schedule H",
        "warnings": [
            "SCHEDULE H PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
            "Long-term proton pump inhibitor use may increase risk of hypomagnesemia and bone fractures.",
        ],
        "contraindications": ["Known hypersensitivity to substituted benzimidazoles"],
        "indications": ["Proton pump inhibitor for gastroesophageal reflux disease (GERD) and peptic ulcers."],
        "jan_aushadhi_code": "PMBJP-00450",
        "jan_aushadhi_generic_name": "Pantoprazole Gastro-resistant Tablets IP 40mg",
        "approx_jan_aushadhi_price_inr": 20.0,
    },
    "cetirizine": {
        "canonical_name": "Cetirizine",
        "ip_monograph": "IP 2022 Monograph, Vol. II, p. 1580",
        "schedule": "Schedule H",
        "warnings": [
            "SCHEDULE H PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
            "May cause drowsiness; caution while driving or operating machinery.",
        ],
        "contraindications": ["End-stage renal disease (CrCl < 10 mL/min)"],
        "indications": ["Second-generation H1-antihistamine for allergic rhinitis and chronic urticaria."],
        "jan_aushadhi_code": "PMBJP-00155",
        "jan_aushadhi_generic_name": "Cetirizine Hydrochloride Tablets IP 10mg",
        "approx_jan_aushadhi_price_inr": 8.0,
    },
    "ibuprofen": {
        "canonical_name": "Ibuprofen",
        "ip_monograph": "IP 2022 Monograph, Vol. II, p. 2280",
        "schedule": "Schedule H",
        "warnings": [
            "SCHEDULE H PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
            "Cardiovascular and gastrointestinal risk: May cause GI bleeding, ulceration, or perforation.",
        ],
        "contraindications": ["Active gastrointestinal bleeding", "Third trimester of pregnancy"],
        "indications": ["Nonsteroidal anti-inflammatory drug (NSAID) for inflammation, pain, and arthritis."],
        "jan_aushadhi_code": "PMBJP-00260",
        "jan_aushadhi_generic_name": "Ibuprofen Tablets IP 400mg",
        "approx_jan_aushadhi_price_inr": 11.0,
    },
}


class IndianReferenceAdapter(BaseReferenceAdapter):
    """Adapter for Indian Pharmacopoeia monographs, CDSCO Drug Schedules, and PMBJP Jan Aushadhi."""

    def __init__(self, custom_registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self._registry = custom_registry or INDIAN_PHARMACOPOEIA_REGISTRY

    @property
    def name(self) -> str:
        return "Indian Pharmacopoeia & CDSCO"

    @property
    def jurisdiction(self) -> str:
        return "IN"

    async def lookup(self, drug_name: str) -> Optional[ReferenceData]:
        """Looks up Indian Pharmacopoeia monograph, schedule status, and Jan Aushadhi generic availability."""
        clean_name = drug_name.strip().lower()
        if not clean_name:
            return None

        # 1. Exact match in Indian Pharmacopoeia Registry
        entry = self._registry.get(clean_name)
        if entry:
            return self._build_reference_data(clean_name, entry)

        # 2. Heuristic check for common Indian regulatory antibiotic and schedule suffixes
        return self._infer_statutory_profile(clean_name)

    def _build_reference_data(self, key: str, entry: Dict[str, Any]) -> ReferenceData:
        canonical_name = entry["canonical_name"]
        jan_aushadhi_note = (
            f"Available under Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP) generic program: "
            f"{entry['jan_aushadhi_generic_name']} (~Rs. {entry['approx_jan_aushadhi_price_inr']:.2f})."
            if "jan_aushadhi_generic_name" in entry
            else "Generic alternatives listed under National List of Essential Medicines (NLEM)."
        )

        indications = list(entry.get("indications", []))
        indications.append(jan_aushadhi_note)

        return ReferenceData(
            source_name="Indian Pharmacopoeia Commission (IPC) / CDSCO",
            source_url="https://ipc.gov.in/",
            source_id=f"IPC-IP2022-{key.upper()}",
            jurisdiction=self.jurisdiction,
            canonical_name=canonical_name,
            indications=indications,
            contraindications=entry.get("contraindications", []),
            warnings=entry.get("warnings", []),
            adverse_reactions=[],
            raw_payload={
                "ip_monograph": entry.get("ip_monograph"),
                "schedule": entry.get("schedule"),
                "jan_aushadhi_code": entry.get("jan_aushadhi_code"),
                "approx_price_inr": entry.get("approx_jan_aushadhi_price_inr"),
            },
        )

    def _infer_statutory_profile(self, clean_name: str) -> Optional[ReferenceData]:
        """Provides statutory fallback for recognized pharmaceutical classes in India."""
        antibiotic_suffixes = ("cillin", "mycin", "floxacin", "penem", "cycline")
        is_antibiotic = any(clean_name.endswith(s) for s in antibiotic_suffixes)

        schedule = "Schedule H1" if is_antibiotic else "Schedule H"
        warnings = [
            f"{schedule.upper()} PRESCRIPTION DRUG - CAUTION: To be sold by retail on the prescription of a Registered Medical Practitioner only.",
        ]
        if is_antibiotic:
            warnings.append(
                "SCHEDULE H1 WARNING: It is dangerous to take this antibiotic preparation except in accordance with medical advice."
            )

        return ReferenceData(
            source_name="Indian Pharmacopoeia Commission (IPC) / CDSCO",
            source_url="https://ipc.gov.in/",
            source_id=f"IPC-REGULATORY-{clean_name.upper()}",
            jurisdiction=self.jurisdiction,
            canonical_name=clean_name.title(),
            indications=["Regulated pharmaceutical substance listed under Drugs & Cosmetics Rules (India)."],
            contraindications=["Hypersensitivity to active compound."],
            warnings=warnings,
            adverse_reactions=[],
            raw_payload={"schedule": schedule, "inferred": True},
        )
