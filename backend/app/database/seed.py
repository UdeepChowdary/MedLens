"""Idempotent clinical database seeder for curated pharmaceutical baseline."""

import asyncio
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_factory, engine, Base
import app.models  # Ensure all model tables are registered on Base.metadata
from app.models.clinical import Source, ClinicalInformation, DrugInteraction
from app.models.product import Product, Ingredient, ProductIngredient, IngredientAlias


async def seed_database(session: AsyncSession) -> Dict[str, int]:
    """Populates curated baseline medicines, monographs, and interactions idempotently."""
    counts = {"sources": 0, "ingredients": 0, "aliases": 0, "products": 0, "interactions": 0}

    # 1. Sources
    sources_data = [
        {
            "id": "src-pubchem",
            "source_name": "National Library of Medicine / PubChem",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-openfda",
            "source_name": "openFDA Drug Product Labels",
            "source_type": "regulatory_label",
            "source_url": "https://open.fda.gov/apis/drug/label/",
            "jurisdiction": "US",
        },
        {
            "id": "src-who",
            "source_name": "WHO Model List of Essential Medicines",
            "source_type": "pharmacopeia",
            "source_url": "https://www.who.int/groups/expert-committee-on-selection-and-use-of-essential-medicines",
            "jurisdiction": "WHO",
        },
    ]

    for s_info in sources_data:
        exists = await session.scalar(select(Source).where(Source.id == s_info["id"]))
        if not exists:
            session.add(Source(**s_info))
            counts["sources"] += 1

    await session.flush()

    # 2. Canonical Ingredients
    ingredients_data = [
        {
            "id": "ing-paracetamol",
            "preferred_name": "Paracetamol",
            "chemical_identifier": "1983",
            "drug_class": "Analgesic, Antipyretic",
            "description": "Reduces pain signals in the nervous system and lowers body temperature via central prostaglandin inhibition.",
            "standard_mechanism": "Inhibition of central cyclooxygenase (COX-3 / COX-1 variants) enzymes with hypothalamic temperature regulation.",
            "max_daily_dose_mg": 4000.0,
        },
        {
            "id": "ing-ibuprofen",
            "preferred_name": "Ibuprofen",
            "chemical_identifier": "3672",
            "drug_class": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
            "description": "Inhibits inflammatory prostaglandins to relieve pain, reduce fever, and diminish swelling.",
            "standard_mechanism": "Non-selective, reversible inhibition of cyclooxygenase enzymes (COX-1 and COX-2).",
            "max_daily_dose_mg": 1200.0,
        },
        {
            "id": "ing-amoxicillin",
            "preferred_name": "Amoxicillin",
            "chemical_identifier": "33613",
            "drug_class": "Beta-lactam Antibiotic (Aminopenicillin)",
            "description": "Bactericidal antibiotic that impedes bacterial cell wall synthesis.",
            "standard_mechanism": "Binds to penicillin-binding proteins (PBPs), inhibiting bacterial transpeptidation.",
            "max_daily_dose_mg": 3000.0,
        },
        {
            "id": "ing-clavulanic-acid",
            "preferred_name": "Clavulanic Acid",
            "chemical_identifier": "28340",
            "drug_class": "Beta-lactamase Inhibitor",
            "description": "Protects beta-lactam antibiotics from enzymatic inactivation by bacterial beta-lactamases.",
            "standard_mechanism": "Suicide inhibitor forming irreversible covalent bond with active site of beta-lactamases.",
            "max_daily_dose_mg": 750.0,
        },
        {
            "id": "ing-cetirizine",
            "preferred_name": "Cetirizine",
            "chemical_identifier": "2678",
            "drug_class": "Second-Generation H1 Antihistamine",
            "description": "Relieves allergic symptoms such as runny nose, itching, and sneezing without heavy sedation.",
            "standard_mechanism": "Selective competitive antagonist of peripheral histamine H1 receptors.",
            "max_daily_dose_mg": 10.0,
        },
    ]

    for ing in ingredients_data:
        exists = await session.scalar(select(Ingredient).where(Ingredient.id == ing["id"]))
        if not exists:
            session.add(Ingredient(**ing))
            counts["ingredients"] += 1

    await session.flush()

    # 3. Aliases
    aliases_data = [
        ("ing-paracetamol", "Acetaminophen", "acetaminophen", "synonym"),
        ("ing-paracetamol", "APAP", "apap", "synonym"),
        ("ing-paracetamol", "Paracetamol IP", "paracetamol ip", "salt_form"),
        ("ing-paracetamol", "Paracetamolo", "paracetamolo", "synonym"),
        ("ing-ibuprofen", "Ibuprofen IP", "ibuprofen ip", "salt_form"),
        ("ing-ibuprofen", "Ibuprofene", "ibuprofene", "synonym"),
        ("ing-amoxicillin", "Amoxicillin Trihydrate", "amoxicillin trihydrate", "salt_form"),
        ("ing-amoxicillin", "Amoxycillin", "amoxycillin", "typo_variant"),
        ("ing-clavulanic-acid", "Clavulanate Potassium", "clavulanate potassium", "salt_form"),
        ("ing-cetirizine", "Cetirizine Hydrochloride", "cetirizine hydrochloride", "salt_form"),
        ("ing-cetirizine", "Cetirizine HCl", "cetirizine hcl", "salt_form"),
    ]

    for ing_id, alias, norm_alias, a_type in aliases_data:
        exists = await session.scalar(
            select(IngredientAlias).where(IngredientAlias.normalized_alias == norm_alias)
        )
        if not exists:
            session.add(
                IngredientAlias(
                    ingredient_id=ing_id,
                    alias_text=alias,
                    normalized_alias=norm_alias,
                    alias_type=a_type,
                )
            )
            counts["aliases"] += 1

    await session.flush()

    # 4. Products & Compositions
    products_data = [
        {
            "product": {
                "id": "dolo-650",
                "brand_name": "Dolo 650",
                "manufacturer": "Micro Labs Ltd",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-paracetamol",
                    "raw_label_text": "Paracetamol IP 650 mg",
                    "strength_numeric": 650.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "calpol-500",
                "brand_name": "Calpol 500",
                "manufacturer": "GSK",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-paracetamol",
                    "raw_label_text": "Paracetamol IP 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "augmentin-625",
                "brand_name": "Augmentin 625 Duo",
                "manufacturer": "GSK",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-amoxicillin",
                    "raw_label_text": "Amoxicillin Trihydrate IP eq. to Amoxicillin 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-clavulanic-acid",
                    "raw_label_text": "Potassium Clavulanate IP eq. to Clavulanic Acid 125 mg",
                    "strength_numeric": 125.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
            ],
        },
        {
            "product": {
                "id": "cetirizine-10",
                "brand_name": "Cetirizine 10mg",
                "manufacturer": "Cipla",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-cetirizine",
                    "raw_label_text": "Cetirizine Hydrochloride IP 10 mg",
                    "strength_numeric": 10.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
    ]

    for p_entry in products_data:
        p_info = p_entry["product"]
        exists = await session.scalar(select(Product).where(Product.id == p_info["id"]))
        if not exists:
            product = Product(**p_info)
            session.add(product)
            counts["products"] += 1
            await session.flush()

            for comp in p_entry["compositions"]:
                session.add(ProductIngredient(product_id=p_info["id"], **comp))

    await session.flush()

    # 5. Clinical Information
    clinical_data = [
        ("product", "dolo-650", "purpose", "Symptomatic relief of fever and mild-to-moderate pain.", "src-openfda"),
        ("product", "dolo-650", "precaution", "Do not exceed maximum daily dose of 4000mg to prevent hepatic injury.", "src-pubchem"),
        ("product", "dolo-650", "contraindication", "Known severe hepatic impairment or active liver disease.", "src-pubchem"),
        ("product", "dolo-650", "adverse_effect", "Nausea, allergic skin reactions, hepatotoxicity in overdose.", "src-openfda"),
        ("ingredient", "ing-paracetamol", "purpose", "Analgesic and antipyretic agent.", "src-who"),
        ("ingredient", "ing-ibuprofen", "precaution", "Use with caution in patients with history of gastrointestinal ulceration.", "src-pubchem"),
        ("ingredient", "ing-amoxicillin", "contraindication", "History of serious hypersensitivity reaction to penicillins.", "src-openfda"),
    ]

    for s_type, s_id, cat, claim, src_id in clinical_data:
        exists = await session.scalar(
            select(ClinicalInformation).where(
                (ClinicalInformation.subject_id == s_id) & (ClinicalInformation.category == cat)
            )
        )
        if not exists:
            session.add(
                ClinicalInformation(
                    subject_type=s_type,
                    subject_id=s_id,
                    category=cat,
                    claim_text=claim,
                    source_id=src_id,
                )
            )

    # 6. Curated Drug-Drug Interactions
    interactions_data = [
        {
            "ingredient_a_id": "ing-paracetamol",
            "ingredient_b_id": "ing-ibuprofen",
            "severity": "minor",
            "clinical_effect": "Generally safe when alternating; monitor renal function and avoid duplicate combination preparations.",
            "source_id": "src-pubchem",
        },
        {
            "ingredient_a_id": "ing-amoxicillin",
            "ingredient_b_id": "ing-clavulanic-acid",
            "severity": "minor",
            "clinical_effect": "Synergistic therapeutic combination; clavulanate protects amoxicillin from beta-lactamase degradation.",
            "source_id": "src-pubchem",
        },
    ]

    for item in interactions_data:
        exists = await session.scalar(
            select(DrugInteraction).where(
                (DrugInteraction.ingredient_a_id == item["ingredient_a_id"])
                & (DrugInteraction.ingredient_b_id == item["ingredient_b_id"])
            )
        )
        if not exists:
            session.add(DrugInteraction(**item))
            counts["interactions"] += 1

    await session.commit()
    return counts


async def main():
    """CLI runner to initialize and seed database."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_factory() as session:
            res = await seed_database(session)
            print("Database initialized and seeded successfully:")
            for k, v in res.items():
                print(f"  - {k}: {v} new records added")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
