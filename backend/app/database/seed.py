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
            "id": "ing-metformin",
            "preferred_name": "Metformin",
            "chemical_identifier": "4091",
            "drug_class": "Biguanide Antidiabetic",
            "description": "Reduces hepatic glucose production and improves insulin sensitivity.",
            "standard_mechanism": "Activates AMPK, inhibiting hepatic gluconeogenesis and increasing peripheral glucose uptake.",
            "max_daily_dose_mg": 2000.0,
        },
        {
            "id": "ing-atorvastatin",
            "preferred_name": "Atorvastatin",
            "chemical_identifier": "60823",
            "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
            "description": "Reduces LDL cholesterol by inhibiting the liver's cholesterol synthesis pathway.",
            "standard_mechanism": "Competitively inhibits 3-hydroxy-3-methylglutaryl-coenzyme A (HMG-CoA) reductase.",
            "max_daily_dose_mg": 80.0,
        },
        {
            "id": "ing-omeprazole",
            "preferred_name": "Omeprazole",
            "chemical_identifier": "4594",
            "drug_class": "Proton Pump Inhibitor (PPI)",
            "description": "Reduces stomach acid production for treatment of GERD and peptic ulcers.",
            "standard_mechanism": "Irreversibly inhibits H+/K+ ATPase (proton pump) in gastric parietal cells.",
            "max_daily_dose_mg": 40.0,
        },
        {
            "id": "ing-azithromycin",
            "preferred_name": "Azithromycin",
            "chemical_identifier": "447043",
            "drug_class": "Macrolide Antibiotic",
            "description": "Broad-spectrum antibiotic effective against respiratory and soft tissue infections.",
            "standard_mechanism": "Binds to 50S ribosomal subunit, inhibiting bacterial protein synthesis.",
            "max_daily_dose_mg": 500.0,
        },
        {
            "id": "ing-pantoprazole",
            "preferred_name": "Pantoprazole",
            "chemical_identifier": "4679",
            "drug_class": "Proton Pump Inhibitor (PPI)",
            "description": "Suppresses excessive stomach acid secretion.",
            "standard_mechanism": "Irreversibly inhibits H+/K+ ATPase enzyme in gastric parietal cells.",
            "max_daily_dose_mg": 40.0,
        },
        {
            "id": "ing-montelukast",
            "preferred_name": "Montelukast",
            "chemical_identifier": "5281040",
            "drug_class": "Leukotriene Receptor Antagonist",
            "description": "Prevents asthma attacks and relieves allergic rhinitis symptoms.",
            "standard_mechanism": "Selectively blocks cysteinyl leukotriene CysLT1 receptors in airways.",
            "max_daily_dose_mg": 10.0,
        },
        {
            "id": "ing-losartan",
            "preferred_name": "Losartan",
            "chemical_identifier": "3961",
            "drug_class": "Angiotensin II Receptor Blocker (ARB)",
            "description": "Treats hypertension and protects kidneys in diabetic patients.",
            "standard_mechanism": "Selectively blocks angiotensin II type 1 (AT1) receptors, causing vasodilation.",
            "max_daily_dose_mg": 100.0,
        },
        {
            "id": "ing-amlodipine",
            "preferred_name": "Amlodipine",
            "chemical_identifier": "2162",
            "drug_class": "Calcium Channel Blocker (Dihydropyridine)",
            "description": "Treats hypertension and angina by relaxing blood vessels.",
            "standard_mechanism": "Blocks L-type calcium channels in vascular smooth muscle, reducing peripheral resistance.",
            "max_daily_dose_mg": 10.0,
        },
        {
            "id": "ing-aspirin",
            "preferred_name": "Aspirin",
            "chemical_identifier": "2244",
            "drug_class": "Salicylate / NSAID / Antiplatelet",
            "description": "Reduces pain, fever, and inflammation; prevents blood clots at low doses.",
            "standard_mechanism": "Irreversibly inhibits COX-1 and COX-2 enzymes; inhibits thromboxane A2 at low doses.",
            "max_daily_dose_mg": 4000.0,
        },
        {
            "id": "ing-domperidone",
            "preferred_name": "Domperidone",
            "chemical_identifier": "3151",
            "drug_class": "Dopamine D2 Receptor Antagonist / Prokinetic",
            "description": "Relieves nausea, vomiting, and bloating by accelerating gastric motility.",
            "standard_mechanism": "Blocks peripheral dopamine D2 receptors in the gut, enhancing peristalsis.",
            "max_daily_dose_mg": 30.0,
        },
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
        # New ingredient aliases
        ("ing-metformin", "Metformin Hydrochloride", "metformin hydrochloride", "salt_form"),
        ("ing-metformin", "Metformin HCl", "metformin hcl", "salt_form"),
        ("ing-atorvastatin", "Atorvastatin Calcium", "atorvastatin calcium", "salt_form"),
        ("ing-atorvastatin", "Atorvastatin Calcium Trihydrate", "atorvastatin calcium trihydrate", "salt_form"),
        ("ing-omeprazole", "Omeprazole IP", "omeprazole ip", "salt_form"),
        ("ing-omeprazole", "Omeprazole Sodium", "omeprazole sodium", "salt_form"),
        ("ing-azithromycin", "Azithromycin Dihydrate", "azithromycin dihydrate", "salt_form"),
        ("ing-azithromycin", "Azithromycin IP", "azithromycin ip", "salt_form"),
        ("ing-pantoprazole", "Pantoprazole Sodium", "pantoprazole sodium", "salt_form"),
        ("ing-pantoprazole", "Pantoprazole Sodium Sesquihydrate", "pantoprazole sodium sesquihydrate", "salt_form"),
        ("ing-montelukast", "Montelukast Sodium", "montelukast sodium", "salt_form"),
        ("ing-losartan", "Losartan Potassium", "losartan potassium", "salt_form"),
        ("ing-amlodipine", "Amlodipine Besylate", "amlodipine besylate", "salt_form"),
        ("ing-amlodipine", "Amlodipine Besilate", "amlodipine besilate", "salt_form"),
        ("ing-aspirin", "Acetylsalicylic Acid", "acetylsalicylic acid", "synonym"),
        ("ing-aspirin", "ASA", "asa", "synonym"),
        ("ing-domperidone", "Domperidone Maleate", "domperidone maleate", "salt_form"),
        # Existing aliases
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
                "id": "glucophage-500",
                "brand_name": "Glucophage 500mg",
                "manufacturer": "Sun Pharma",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-metformin",
                    "raw_label_text": "Metformin Hydrochloride IP 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "glucophage-1000",
                "brand_name": "Glucophage 1000mg",
                "manufacturer": "Sun Pharma",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-metformin",
                    "raw_label_text": "Metformin Hydrochloride IP 1000 mg",
                    "strength_numeric": 1000.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "lipitor-10",
                "brand_name": "Lipitor 10mg",
                "manufacturer": "Pfizer",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-atorvastatin",
                    "raw_label_text": "Atorvastatin Calcium 10 mg",
                    "strength_numeric": 10.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "storvas-20",
                "brand_name": "Storvas 20",
                "manufacturer": "Sun Pharma",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-atorvastatin",
                    "raw_label_text": "Atorvastatin Calcium 20 mg",
                    "strength_numeric": 20.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "omez-20",
                "brand_name": "Omez 20mg",
                "manufacturer": "Dr. Reddy's",
                "dosage_form": "Capsule",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-omeprazole",
                    "raw_label_text": "Omeprazole IP 20 mg",
                    "strength_numeric": 20.0,
                    "strength_unit": "mg",
                    "strength_basis": "per capsule",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "zithromax-500",
                "brand_name": "Zithromax 500mg",
                "manufacturer": "Pfizer",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-azithromycin",
                    "raw_label_text": "Azithromycin Dihydrate IP 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "azee-500",
                "brand_name": "Azee 500",
                "manufacturer": "Cipla",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-azithromycin",
                    "raw_label_text": "Azithromycin IP 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "pantodac-40",
                "brand_name": "Pantodac 40",
                "manufacturer": "Zydus",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-pantoprazole",
                    "raw_label_text": "Pantoprazole Sodium Sesquihydrate IP 40 mg",
                    "strength_numeric": 40.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "pan-40",
                "brand_name": "Pan-40",
                "manufacturer": "Alkem",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-pantoprazole",
                    "raw_label_text": "Pantoprazole Sodium IP 40 mg",
                    "strength_numeric": 40.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "montek-10",
                "brand_name": "Montek LC 10",
                "manufacturer": "Sun Pharma",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-montelukast",
                    "raw_label_text": "Montelukast Sodium 10 mg",
                    "strength_numeric": 10.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-cetirizine",
                    "raw_label_text": "Cetirizine Hydrochloride 5 mg",
                    "strength_numeric": 5.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
            ],
        },
        {
            "product": {
                "id": "losartan-50",
                "brand_name": "Losartan 50",
                "manufacturer": "Cipla",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-losartan",
                    "raw_label_text": "Losartan Potassium 50 mg",
                    "strength_numeric": 50.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "amlodac-5",
                "brand_name": "Amlodac 5",
                "manufacturer": "Zydus",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-amlodipine",
                    "raw_label_text": "Amlodipine Besylate 5 mg",
                    "strength_numeric": 5.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "ecosprin-75",
                "brand_name": "Ecosprin 75",
                "manufacturer": "USV Ltd",
                "dosage_form": "Tablet - Enteric Coated",
                "route": "Oral",
                "release_type": "Enteric Coated",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-aspirin",
                    "raw_label_text": "Aspirin 75 mg",
                    "strength_numeric": 75.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "crocin-650",
                "brand_name": "Crocin 650",
                "manufacturer": "GSK",
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
                "id": "paracip-500",
                "brand_name": "Paracip 500",
                "manufacturer": "Cipla",
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
                "id": "brufen-400",
                "brand_name": "Brufen 400",
                "manufacturer": "Abbott",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-ibuprofen",
                    "raw_label_text": "Ibuprofen IP 400 mg",
                    "strength_numeric": 400.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "combiflam",
                "brand_name": "Combiflam",
                "manufacturer": "Sanofi",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-ibuprofen",
                    "raw_label_text": "Ibuprofen IP 400 mg",
                    "strength_numeric": 400.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-paracetamol",
                    "raw_label_text": "Paracetamol IP 325 mg",
                    "strength_numeric": 325.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                },
            ],
        },
        {
            "product": {
                "id": "vomistop-10",
                "brand_name": "Vomistop 10",
                "manufacturer": "Meyer",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-domperidone",
                    "raw_label_text": "Domperidone 10 mg",
                    "strength_numeric": 10.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
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
        # New clinical info for new products and ingredients
        ("product", "glucophage-500", "purpose", "Lowers blood glucose levels in type 2 diabetes mellitus.", "src-openfda"),
        ("product", "glucophage-500", "precaution", "Monitor renal function before initiating therapy; contraindicated in eGFR < 30 mL/min/1.73m².", "src-openfda"),
        ("ingredient", "ing-metformin", "contraindication", "Renal impairment (eGFR < 30), hepatic failure, or conditions that may cause lactic acidosis.", "src-pubchem"),
        ("product", "lipitor-10", "purpose", "Reduction of elevated LDL-C, total-C, triglycerides, and apolipoprotein B.", "src-openfda"),
        ("ingredient", "ing-atorvastatin", "contraindication", "Active liver disease or unexplained persistent elevations in serum transaminases. Pregnancy.", "src-pubchem"),
        ("product", "omez-20", "purpose", "Treatment of duodenal ulcer, gastric ulcer, GERD, and Helicobacter pylori eradication.", "src-openfda"),
        ("product", "zithromax-500", "purpose", "Treatment of community-acquired pneumonia, sinusitis, pharyngitis, and skin infections.", "src-openfda"),
        ("ingredient", "ing-azithromycin", "contraindication", "Known hypersensitivity to azithromycin, erythromycin, or any macrolide antibiotic.", "src-pubchem"),
        ("product", "ecosprin-75", "purpose", "Low-dose antiplatelet therapy for prevention of myocardial infarction and ischemic stroke.", "src-openfda"),
        ("ingredient", "ing-aspirin", "precaution", "Avoid in children under 16 with viral illnesses (Reye syndrome risk). Use with caution in peptic ulcer disease.", "src-pubchem"),
        ("product", "combiflam", "purpose", "Short-term relief of moderate acute pain and fever.", "src-openfda"),
        ("product", "combiflam", "precaution", "Contains both Ibuprofen and Paracetamol; do not combine with other products containing these actives.", "src-openfda"),
        ("product", "montek-10", "purpose", "Prophylaxis of asthma and relief of seasonal allergic rhinitis symptoms.", "src-openfda"),
        ("ingredient", "ing-montelukast", "contraindication", "Known hypersensitivity to montelukast or any excipient.", "src-pubchem"),
        # Existing clinical info
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
        # New interactions
        {
            "ingredient_a_id": "ing-aspirin",
            "ingredient_b_id": "ing-ibuprofen",
            "severity": "moderate",
            "clinical_effect": "Concurrent use may reduce aspirin's antiplatelet effect. Ibuprofen may competitively inhibit COX-1 binding of aspirin.",
            "source_id": "src-pubchem",
        },
        {
            "ingredient_a_id": "ing-metformin",
            "ingredient_b_id": "ing-omeprazole",
            "severity": "minor",
            "clinical_effect": "Proton pump inhibitors may modestly increase metformin plasma levels via OCT2/MATE transporter inhibition. Monitor for hypoglycemia.",
            "source_id": "src-pubchem",
        },
        {
            "ingredient_a_id": "ing-atorvastatin",
            "ingredient_b_id": "ing-azithromycin",
            "severity": "minor",
            "clinical_effect": "Azithromycin may slightly increase atorvastatin exposure via CYP3A4 inhibition. Monitor for myopathy symptoms.",
            "source_id": "src-pubchem",
        },
        {
            "ingredient_a_id": "ing-amlodipine",
            "ingredient_b_id": "ing-losartan",
            "severity": "minor",
            "clinical_effect": "Combination is commonly prescribed for hypertension management; additive antihypertensive effects. Monitor blood pressure.",
            "source_id": "src-pubchem",
        },
        # Existing interactions
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
