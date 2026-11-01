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

    # 1. Sources (ML-013: Deep section-level monograph and regulatory citations)
    sources_data = [
        # Baseline general authority references
        {
            "id": "src-pubchem",
            "source_name": "National Library of Medicine / PubChem Comprehensive Substance Directory",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-openfda",
            "source_name": "openFDA Drug Product Labels Database",
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
        # Deep-linked Verified Monograph Sources per Active Ingredient
        {
            "id": "src-pubchem-paracetamol",
            "source_name": "PubChem Compound (CID 1983) - Paracetamol / Acetaminophen Safety Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/1983#section=Safety-and-Hazards",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-who-paracetamol",
            "source_name": "WHO Model List of Essential Medicines (23rd List, 2023) - Paracetamol",
            "source_type": "pharmacopeia",
            "source_url": "https://list.essentialmeds.org/medicines/18",
            "jurisdiction": "WHO",
        },
        {
            "id": "src-dailymed-paracetamol",
            "source_name": "DailyMed - Acetaminophen Tablet 500mg/650mg FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c29ee2d9-130a-4da2-ac88-b27b3b4ff97e#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-ipc-paracetamol",
            "source_name": "Indian Pharmacopoeia Commission (IPC) - Paracetamol Tablets IP Monograph",
            "source_type": "pharmacopeia",
            "source_url": "https://ipc.gov.in/",
            "jurisdiction": "IN",
        },
        {
            "id": "src-pubchem-ibuprofen",
            "source_name": "PubChem Compound (CID 3672) - Ibuprofen Safety and Warnings Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/3672#section=Warnings",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-ibuprofen",
            "source_name": "DailyMed - Ibuprofen Tablet 400mg FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3be7e722-1d54-474d-b6a9-858fc92fb384#section-5",
            "jurisdiction": "US",
        },
        {
            "id": "src-dailymed-combiflam",
            "source_name": "DailyMed - Ibuprofen and Acetaminophen Co-administration Monograph",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=25c04b89-a2e6-42bb-92ef-cce360db238d#section-5",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-metformin",
            "source_name": "PubChem Compound (CID 4091) - Metformin Hydrochloride Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/4091#section=Contraindications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-metformin",
            "source_name": "DailyMed - Glucophage (Metformin HCl) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=02f107f9-81a0-47bf-a1fd-c4e94119d832#section-4",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-atorvastatin",
            "source_name": "PubChem Compound (CID 60823) - Atorvastatin Calcium Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/60823#section=Contraindications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-atorvastatin",
            "source_name": "DailyMed - Lipitor (Atorvastatin Calcium) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b9c4fcfb-6f8e-4a6c-9a4d-080c98f8253d#section-4",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-omeprazole",
            "source_name": "PubChem Compound (CID 4594) - Omeprazole Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/4594#section=Indications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-omeprazole",
            "source_name": "DailyMed - Prilosec / Omeprazole Delayed-Release Capsule FDA Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4270d180-2c78-4ea7-9092-23fcfb6ab73c#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-azithromycin",
            "source_name": "PubChem Compound (CID 447043) - Azithromycin Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/447043#section=Contraindications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-azithromycin",
            "source_name": "DailyMed - Zithromax (Azithromycin) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=072a74c7-e6f9-467a-bb80-e3746a51d953#section-4",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-pantoprazole",
            "source_name": "PubChem Compound (CID 4679) - Pantoprazole Sodium Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/4679#section=Pharmacology-and-Biochemistry",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-pantoprazole",
            "source_name": "DailyMed - Protonix (Pantoprazole Sodium) Delayed-Release FDA Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=033bf9e4-3996-41b9-8c46-921d152a5124#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-montelukast",
            "source_name": "PubChem Compound (CID 5281040) - Montelukast Sodium Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/5281040#section=Contraindications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-montelukast",
            "source_name": "DailyMed - Singulair (Montelukast Sodium) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=361ebc6b-ee0b-4f4a-85d1-ea91bf14070a#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-aspirin",
            "source_name": "PubChem Compound (CID 2244) - Aspirin / Acetylsalicylic Acid Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/2244#section=Warnings",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-aspirin",
            "source_name": "DailyMed - Aspirin Enteric Coated Tablet FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=05d76295-a4b5-412e-a5fa-cb2ee8979354#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-amoxicillin",
            "source_name": "PubChem Compound (CID 33613) - Amoxicillin Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/33613#section=Contraindications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-amoxicillin",
            "source_name": "DailyMed - Amoxil (Amoxicillin) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e0d778d9-299f-4318-8686-efb0451cf18e#section-4",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-clavulanic-acid",
            "source_name": "PubChem Compound (CID 28340) - Clavulanic Acid / Clavulanate Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/28340#section=Mechanism-of-Action",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-augmentin",
            "source_name": "DailyMed - Augmentin (Amoxicillin and Clavulanate Potassium) FDA Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d4b2e88a-ba0f-48e0-bb15-38b4f1b4c3e8#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-cetirizine",
            "source_name": "PubChem Compound (CID 2678) - Cetirizine Dihydrochloride Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/2678#section=Indications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-cetirizine",
            "source_name": "DailyMed - Zyrtec (Cetirizine HCl) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=29b9cf99-63ff-4cfc-8ff2-d04b30e46b3f#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-domperidone",
            "source_name": "PubChem Compound (CID 3151) - Domperidone Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/3151#section=Pharmacology-and-Biochemistry",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-cdsco-domperidone",
            "source_name": "CDSCO / National Formulary of India - Domperidone Prokinetic Monograph",
            "source_type": "regulatory_label",
            "source_url": "https://cdsco.gov.in/",
            "jurisdiction": "IN",
        },
        {
            "id": "src-pubchem-diphenhydramine",
            "source_name": "PubChem Compound (CID 3100) - Diphenhydramine Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/3100#section=Indications",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-benadryl",
            "source_name": "DailyMed - Benadryl (Diphenhydramine HCl) FDA Structured Product Label",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7f0cba1e-fc3f-42a0-ba4c-0d04fb4ffc20#section-1",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-ammonium-chloride",
            "source_name": "PubChem Compound (CID 25517) - Ammonium Chloride Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/25517#section=Use-and-Manufacturing",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-pubchem-sodium-citrate",
            "source_name": "PubChem Compound (CID 6224) - Sodium Citrate Monograph",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/6224#section=Pharmacology-and-Biochemistry",
            "jurisdiction": "GLOBAL",
        },
        # Deep Interaction Sources (ML-013)
        {
            "id": "src-fda-interaction-aspirin-ibuprofen",
            "source_name": "FDA Drug Safety Communication: Concomitant Use of Ibuprofen and Low-Dose Aspirin",
            "source_type": "regulatory_label",
            "source_url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-interaction-between-concomitant-use-ibuprofen-and-low-dose-aspirin",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-interaction-metformin-omeprazole",
            "source_name": "PubChem Compound (CID 4091) Drug Interactions: Metformin with Omeprazole (OCT2 Transporter)",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/4091#section=Drug-Interactions",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-pubchem-interaction-atorvastatin-azithromycin",
            "source_name": "PubChem Compound (CID 60823) Drug Interactions: Atorvastatin with Azithromycin (CYP3A4)",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/60823#section=Drug-Interactions",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-interaction-amlodipine-losartan",
            "source_name": "DailyMed - Cozaar / Norvasc (Amlodipine and Losartan Antihypertensive Concomitance)",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1f9dca12-ff54-4f24-9dfc-5b5ea84742f5#section-7",
            "jurisdiction": "US",
        },
        {
            "id": "src-pubchem-interaction-paracetamol-ibuprofen",
            "source_name": "PubChem Compound (CID 1983) Drug Interactions: Paracetamol with Ibuprofen",
            "source_type": "monograph",
            "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/1983#section=Drug-Interactions",
            "jurisdiction": "GLOBAL",
        },
        {
            "id": "src-dailymed-interaction-amox-clav",
            "source_name": "DailyMed - Augmentin (Amoxicillin and Clavulanate Potassium Synergy Mechanism)",
            "source_type": "regulatory_label",
            "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d4b2e88a-ba0f-48e0-bb15-38b4f1b4c3e8#section-12.4",
            "jurisdiction": "US",
        },
        {
            "id": "src-cdsco-interaction-pantoprazole-domperidone",
            "source_name": "CDSCO - Fixed Dose Combination: Pantoprazole 40mg + Domperidone 30mg SR",
            "source_type": "regulatory_label",
            "source_url": "https://cdsco.gov.in/",
            "jurisdiction": "IN",
        },
    ]

    for s_info in sources_data:
        exists = await session.scalar(select(Source).where(Source.id == s_info["id"]))
        if not exists:
            session.add(Source(**s_info))
            counts["sources"] += 1
        else:
            if exists.source_url != s_info["source_url"] or exists.source_name != s_info["source_name"]:
                exists.source_url = s_info["source_url"]
                exists.source_name = s_info["source_name"]
                exists.source_type = s_info.get("source_type", exists.source_type)
                exists.jurisdiction = s_info.get("jurisdiction", exists.jurisdiction)

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
        {
            "id": "ing-diphenhydramine",
            "preferred_name": "Diphenhydramine",
            "chemical_identifier": "3100",
            "drug_class": "Ethanolamine Antihistamine / Antitussive",
            "description": "Relieves cough, allergy symptoms, and promotes bronchial comfort.",
            "standard_mechanism": "Competitively blocks central and peripheral H1 histamine receptors and muscarinic receptors.",
            "max_daily_dose_mg": 300.0,
        },
        {
            "id": "ing-ammonium-chloride",
            "preferred_name": "Ammonium Chloride",
            "chemical_identifier": "25517",
            "drug_class": "Expectorant",
            "description": "Stimulates respiratory tract fluid production, thinning mucus for easier clearance.",
            "standard_mechanism": "Reflex mucociliary secretion stimulation via gastric-vagal pathway.",
            "max_daily_dose_mg": 1000.0,
        },
        {
            "id": "ing-sodium-citrate",
            "preferred_name": "Sodium Citrate",
            "chemical_identifier": "6224",
            "drug_class": "Mucolytic / Systemic Alkalinizer",
            "description": "Liquefies tenacious bronchial secretions and reduces cough viscosity.",
            "standard_mechanism": "Osmotic liquification of bronchial secretions and mild systemic alkalinization.",
            "max_daily_dose_mg": 3000.0,
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
        ("ing-metformin", "Glycomet", "glycomet", "brand_synonym"),
        ("ing-atorvastatin", "Atorvastatin Calcium", "atorvastatin calcium", "salt_form"),
        ("ing-atorvastatin", "Atorvastatin Calcium Trihydrate", "atorvastatin calcium trihydrate", "salt_form"),
        ("ing-omeprazole", "Omeprazole IP", "omeprazole ip", "salt_form"),
        ("ing-omeprazole", "Omeprazole Sodium", "omeprazole sodium", "salt_form"),
        ("ing-azithromycin", "Azithromycin Dihydrate", "azithromycin dihydrate", "salt_form"),
        ("ing-azithromycin", "Azithromycin IP", "azithromycin ip", "salt_form"),
        ("ing-azithromycin", "Azithral", "azithral", "brand_synonym"),
        ("ing-pantoprazole", "Pantoprazole Sodium", "pantoprazole sodium", "salt_form"),
        ("ing-pantoprazole", "Pantoprazole Sodium Sesquihydrate", "pantoprazole sodium sesquihydrate", "salt_form"),
        ("ing-pantoprazole", "Pan", "pan", "brand_synonym"),
        ("ing-montelukast", "Montelukast Sodium", "montelukast sodium", "salt_form"),
        ("ing-montelukast", "Montair", "montair", "brand_synonym"),
        ("ing-losartan", "Losartan Potassium", "losartan potassium", "salt_form"),
        ("ing-amlodipine", "Amlodipine Besylate", "amlodipine besylate", "salt_form"),
        ("ing-amlodipine", "Amlodipine Besilate", "amlodipine besilate", "salt_form"),
        ("ing-aspirin", "Acetylsalicylic Acid", "acetylsalicylic acid", "synonym"),
        ("ing-aspirin", "ASA", "asa", "synonym"),
        ("ing-domperidone", "Domperidone Maleate", "domperidone maleate", "salt_form"),
        ("ing-diphenhydramine", "Diphenhydramine Hydrochloride", "diphenhydramine hydrochloride", "salt_form"),
        ("ing-diphenhydramine", "Diphenhydramine HCl", "diphenhydramine hcl", "salt_form"),
        ("ing-diphenhydramine", "Diphenhydramine IP", "diphenhydramine ip", "salt_form"),
        ("ing-ammonium-chloride", "Ammonium Chloride IP", "ammonium chloride ip", "salt_form"),
        ("ing-sodium-citrate", "Sodium Citrate IP", "sodium citrate ip", "salt_form"),
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
        # Authentic Indian Packaging Brands (Batch 1 & 2)
        {
            "product": {
                "id": "azithral-500",
                "brand_name": "Azithral 500",
                "manufacturer": "Alembic Pharmaceuticals Ltd",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-azithromycin",
                    "raw_label_text": "Azithromycin IP eq. to Azithromycin 500 mg",
                    "strength_numeric": 500.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "pan-d",
                "brand_name": "Pan-D",
                "manufacturer": "Alkem Laboratories Ltd",
                "dosage_form": "Capsule",
                "route": "Oral",
                "release_type": "Sustained Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-pantoprazole",
                    "raw_label_text": "Pantoprazole Sodium IP eq. to Pantoprazole 40 mg (Enteric Coated)",
                    "strength_numeric": 40.0,
                    "strength_unit": "mg",
                    "strength_basis": "per capsule",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-domperidone",
                    "raw_label_text": "Domperidone IP 30 mg (Sustained Release)",
                    "strength_numeric": 30.0,
                    "strength_unit": "mg",
                    "strength_basis": "per capsule",
                    "is_active": True,
                },
            ],
        },
        {
            "product": {
                "id": "glycomet-500",
                "brand_name": "Glycomet 500",
                "manufacturer": "USV Pvt Ltd",
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
                "id": "montair-10",
                "brand_name": "Montair 10",
                "manufacturer": "Cipla Ltd",
                "dosage_form": "Tablet",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-montelukast",
                    "raw_label_text": "Montelukast Sodium IP eq. to Montelukast 10 mg",
                    "strength_numeric": 10.0,
                    "strength_unit": "mg",
                    "strength_basis": "per tablet",
                    "is_active": True,
                }
            ],
        },
        {
            "product": {
                "id": "benadryl-syrup",
                "brand_name": "Benadryl Cough Formula",
                "manufacturer": "Johnson & Johnson Pvt Ltd",
                "dosage_form": "Syrup",
                "route": "Oral",
                "release_type": "Immediate Release",
                "country_code": "IN",
            },
            "compositions": [
                {
                    "ingredient_id": "ing-diphenhydramine",
                    "raw_label_text": "Diphenhydramine Hydrochloride IP 14.08 mg",
                    "strength_numeric": 14.08,
                    "strength_unit": "mg",
                    "strength_basis": "per 5 ml",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-ammonium-chloride",
                    "raw_label_text": "Ammonium Chloride IP 138 mg",
                    "strength_numeric": 138.0,
                    "strength_unit": "mg",
                    "strength_basis": "per 5 ml",
                    "is_active": True,
                },
                {
                    "ingredient_id": "ing-sodium-citrate",
                    "raw_label_text": "Sodium Citrate IP 57.03 mg",
                    "strength_numeric": 57.03,
                    "strength_unit": "mg",
                    "strength_basis": "per 5 ml",
                    "is_active": True,
                },
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

    # 5. Clinical Information (ML-013: Deep section-level source provenance)
    clinical_data = [
        # Dolo 650
        ("product", "dolo-650", "purpose", "Symptomatic relief of fever and mild-to-moderate pain.", "src-dailymed-paracetamol"),
        ("product", "dolo-650", "precaution", "Do not exceed maximum daily dose of 4000mg to prevent hepatic injury.", "src-pubchem-paracetamol"),
        ("product", "dolo-650", "contraindication", "Known severe hepatic impairment or active liver disease.", "src-pubchem-paracetamol"),
        ("product", "dolo-650", "adverse_effect", "Nausea, allergic skin reactions, hepatotoxicity in overdose.", "src-dailymed-paracetamol"),

        # Combiflam
        ("product", "combiflam", "purpose", "Short-term relief of acute moderate pain and inflammatory fever.", "src-dailymed-combiflam"),
        ("product", "combiflam", "precaution", "Contains both Ibuprofen (400mg) and Paracetamol (325mg); do not combine with other products containing paracetamol or NSAIDs.", "src-dailymed-combiflam"),
        ("product", "combiflam", "contraindication", "Active peptic ulcer disease, severe renal impairment, or history of NSAID-induced asthma.", "src-pubchem-ibuprofen"),

        # Pan 40 & Pan-D
        ("product", "pan-40", "purpose", "Short-term treatment of gastroesophageal reflux disease (GERD) and healing of erosive esophagitis.", "src-dailymed-pantoprazole"),
        ("product", "pan-40", "precaution", "Prolonged proton pump inhibitor therapy may increase risk of hypomagnesemia and bone fractures.", "src-dailymed-pantoprazole"),
        ("product", "pan-d", "purpose", "Treatment of gastroesophageal reflux disease associated with delayed gastric emptying or gastroparesis.", "src-cdsco-interaction-pantoprazole-domperidone"),
        ("product", "pan-d", "precaution", "Contains sustained-release domperidone pellets; capsule must be swallowed whole without crushing or chewing.", "src-cdsco-interaction-pantoprazole-domperidone"),

        # Azithral 500
        ("product", "azithral-500", "purpose", "Treatment of community-acquired pneumonia, sinusitis, pharyngitis, and skin infections.", "src-dailymed-azithromycin"),
        ("product", "azithral-500", "precaution", "May prolong cardiac QT interval; use caution in patients with proarrhythmic conditions.", "src-dailymed-azithromycin"),

        # Glycomet 500 & Glucophage
        ("product", "glycomet-500", "purpose", "Improve glycemic control in adults with type 2 diabetes mellitus.", "src-dailymed-metformin"),
        ("product", "glycomet-500", "precaution", "Monitor renal function (eGFR); contraindicated in severe renal impairment (eGFR < 30 mL/min).", "src-dailymed-metformin"),
        ("product", "glucophage-500", "purpose", "Lowers blood glucose levels in type 2 diabetes mellitus.", "src-dailymed-metformin"),
        ("product", "glucophage-500", "precaution", "Monitor renal function before initiating therapy; contraindicated in eGFR < 30 mL/min/1.73m².", "src-dailymed-metformin"),

        # Montair 10 & Montek LC
        ("product", "montair-10", "purpose", "Prophylaxis and chronic treatment of asthma and relief of seasonal allergic rhinitis.", "src-dailymed-montelukast"),
        ("product", "montair-10", "precaution", "Monitor for neuropsychiatric changes; not indicated for the reversal of acute bronchospasm.", "src-dailymed-montelukast"),
        ("product", "montek-10", "purpose", "Prophylaxis of asthma and dual relief of seasonal allergic rhinitis symptoms.", "src-dailymed-montelukast"),

        # Benadryl Cough Formula
        ("product", "benadryl-syrup", "purpose", "Temporary relief of cough due to minor throat and bronchial irritation.", "src-dailymed-benadryl"),
        ("product", "benadryl-syrup", "precaution", "May cause marked drowsiness; avoid driving, machinery, or alcoholic beverages.", "src-dailymed-benadryl"),

        # Augmentin 625 Duo
        ("product", "augmentin-625", "purpose", "Treatment of lower respiratory, otitis media, sinusitis, skin, and urinary tract infections.", "src-dailymed-augmentin"),
        ("product", "augmentin-625", "precaution", "Carefully adjust dose in severe renal impairment; risk of Clostridioides difficile colitis.", "src-dailymed-augmentin"),

        # Cetirizine 10mg
        ("product", "cetirizine-10", "purpose", "Relief of symptoms associated with seasonal and perennial allergic rhinitis and chronic urticaria.", "src-dailymed-cetirizine"),
        ("product", "cetirizine-10", "precaution", "Use caution when driving or operating machinery due to potential somnolence.", "src-dailymed-cetirizine"),

        # Ecosprin 75
        ("product", "ecosprin-75", "purpose", "Low-dose antiplatelet therapy for secondary prevention of myocardial infarction and ischemic stroke.", "src-dailymed-aspirin"),
        ("product", "ecosprin-75", "precaution", "Use with caution in patients with history of gastrointestinal ulceration or bleeding disorders.", "src-pubchem-aspirin"),

        # Omez 20
        ("product", "omez-20", "purpose", "Treatment of duodenal ulcer, gastric ulcer, GERD, and Helicobacter pylori eradication.", "src-dailymed-omeprazole"),

        # Lipitor 10
        ("product", "lipitor-10", "purpose", "Reduction of elevated LDL-C, total-C, triglycerides, and apolipoprotein B.", "src-dailymed-atorvastatin"),

        # Canonical Ingredient Monographs
        ("ingredient", "ing-paracetamol", "purpose", "Analgesic and antipyretic agent.", "src-who-paracetamol"),
        ("ingredient", "ing-paracetamol", "contraindication", "Severe hepatic impairment or severe active liver disease.", "src-pubchem-paracetamol"),
        ("ingredient", "ing-paracetamol", "precaution", "Total daily intake must not exceed 4,000 mg across all oral and intravenous combination sources.", "src-pubchem-paracetamol"),

        ("ingredient", "ing-ibuprofen", "purpose", "Non-steroidal anti-inflammatory drug providing analgesia, antipyresis, and anti-inflammatory activity.", "src-pubchem-ibuprofen"),
        ("ingredient", "ing-ibuprofen", "precaution", "Use with caution in patients with history of gastrointestinal ulceration or renal impairment.", "src-pubchem-ibuprofen"),
        ("ingredient", "ing-ibuprofen", "contraindication", "Known allergy to aspirin or other NSAIDs, active gastrointestinal bleeding, or third-trimester pregnancy.", "src-dailymed-ibuprofen"),

        ("ingredient", "ing-amoxicillin", "purpose", "Broad-spectrum bactericidal penicillin antibiotic.", "src-pubchem-amoxicillin"),
        ("ingredient", "ing-amoxicillin", "contraindication", "History of serious hypersensitivity reaction (anaphylaxis) to penicillins or beta-lactam antibiotics.", "src-dailymed-amoxicillin"),

        ("ingredient", "ing-clavulanic-acid", "purpose", "Beta-lactamase inhibitor preventing enzymatic degradation of beta-lactams.", "src-pubchem-clavulanic-acid"),

        ("ingredient", "ing-metformin", "purpose", "Biguanide antihyperglycemic improving peripheral insulin sensitivity.", "src-pubchem-metformin"),
        ("ingredient", "ing-metformin", "contraindication", "Severe renal impairment (eGFR < 30 mL/min/1.73m²), metabolic acidosis, or conditions predisposing to lactic acidosis.", "src-pubchem-metformin"),

        ("ingredient", "ing-atorvastatin", "purpose", "HMG-CoA reductase inhibitor lowering atherogenic lipoprotein levels.", "src-pubchem-atorvastatin"),
        ("ingredient", "ing-atorvastatin", "contraindication", "Active liver disease, unexplained persistent transaminase elevations, or pregnancy.", "src-pubchem-atorvastatin"),

        ("ingredient", "ing-omeprazole", "purpose", "Suppresses gastric acid secretion via selective H+/K+ ATPase inhibition.", "src-pubchem-omeprazole"),
        ("ingredient", "ing-omeprazole", "contraindication", "Known hypersensitivity to omeprazole or substituted benzimidazoles.", "src-pubchem-omeprazole"),

        ("ingredient", "ing-pantoprazole", "purpose", "Suppresses gastric acid secretion via irreversible H+/K+ ATPase inhibition.", "src-pubchem-pantoprazole"),
        ("ingredient", "ing-pantoprazole", "contraindication", "Known hypersensitivity to pantoprazole or substituted benzimidazoles.", "src-pubchem-pantoprazole"),

        ("ingredient", "ing-azithromycin", "purpose", "Macrolide antibiotic inhibiting bacterial 50S ribosomal protein synthesis.", "src-pubchem-azithromycin"),
        ("ingredient", "ing-azithromycin", "contraindication", "Known hypersensitivity to azithromycin, erythromycin, or any macrolide antibiotic.", "src-pubchem-azithromycin"),

        ("ingredient", "ing-montelukast", "purpose", "Cysteinyl leukotriene receptor antagonist inhibiting bronchial smooth muscle bronchoconstriction.", "src-pubchem-montelukast"),
        ("ingredient", "ing-montelukast", "contraindication", "Known hypersensitivity to montelukast sodium or any formulation excipient.", "src-pubchem-montelukast"),

        ("ingredient", "ing-aspirin", "purpose", "Irreversible cyclooxygenase-1 inhibitor preventing platelet thromboxane A2 synthesis.", "src-pubchem-aspirin"),
        ("ingredient", "ing-aspirin", "precaution", "Avoid in children under 16 with viral illnesses (Reye syndrome risk). Use with caution in peptic ulcer disease.", "src-pubchem-aspirin"),

        ("ingredient", "ing-cetirizine", "purpose", "Selective peripheral histamine H1 receptor antagonist.", "src-pubchem-cetirizine"),
        ("ingredient", "ing-cetirizine", "contraindication", "End-stage renal disease (eGFR < 10 mL/min) or patients undergoing hemodialysis.", "src-pubchem-cetirizine"),

        ("ingredient", "ing-domperidone", "purpose", "Peripheral dopamine D2 receptor antagonist promoting upper gastrointestinal motility.", "src-pubchem-domperidone"),

        ("ingredient", "ing-diphenhydramine", "purpose", "First-generation antihistamine with central and peripheral anticholinergic and antitussive effects.", "src-pubchem-diphenhydramine"),
        ("ingredient", "ing-diphenhydramine", "contraindication", "Concomitant use of monoamine oxidase inhibitors (MAOIs) or narrow-angle glaucoma.", "src-pubchem-diphenhydramine"),
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
        else:
            if exists.source_id != src_id or exists.claim_text != claim:
                exists.source_id = src_id
                exists.claim_text = claim

    # 6. Curated Drug-Drug Interactions (ML-013: Deep section-level source provenance)
    interactions_data = [
        {
            "ingredient_a_id": "ing-aspirin",
            "ingredient_b_id": "ing-ibuprofen",
            "severity": "moderate",
            "clinical_effect": "Concurrent use may reduce aspirin's cardioprotective antiplatelet effect. Ibuprofen competitively impedes irreversible platelet COX-1 acetylation by aspirin.",
            "source_id": "src-fda-interaction-aspirin-ibuprofen",
        },
        {
            "ingredient_a_id": "ing-metformin",
            "ingredient_b_id": "ing-omeprazole",
            "severity": "minor",
            "clinical_effect": "Proton pump inhibitors may modestly increase metformin exposure via renal OCT2/MATE transporter inhibition. Monitor for hypoglycemia.",
            "source_id": "src-pubchem-interaction-metformin-omeprazole",
        },
        {
            "ingredient_a_id": "ing-atorvastatin",
            "ingredient_b_id": "ing-azithromycin",
            "severity": "minor",
            "clinical_effect": "Azithromycin may slightly increase atorvastatin exposure via CYP3A4 inhibition. Monitor for unexplained muscle pain or myopathy symptoms.",
            "source_id": "src-pubchem-interaction-atorvastatin-azithromycin",
        },
        {
            "ingredient_a_id": "ing-amlodipine",
            "ingredient_b_id": "ing-losartan",
            "severity": "minor",
            "clinical_effect": "Combination is commonly prescribed for hypertension management; additive antihypertensive effects. Monitor blood pressure for hypotension.",
            "source_id": "src-dailymed-interaction-amlodipine-losartan",
        },
        {
            "ingredient_a_id": "ing-paracetamol",
            "ingredient_b_id": "ing-ibuprofen",
            "severity": "minor",
            "clinical_effect": "Alternating or combining paracetamol and ibuprofen provides effective analgesia; monitor renal function and avoid duplicate combination preparations or exceeding maximum daily limits.",
            "source_id": "src-pubchem-interaction-paracetamol-ibuprofen",
        },
        {
            "ingredient_a_id": "ing-amoxicillin",
            "ingredient_b_id": "ing-clavulanic-acid",
            "severity": "minor",
            "clinical_effect": "Synergistic therapeutic combination; clavulanate protects amoxicillin from bacterial beta-lactamase enzymatic degradation.",
            "source_id": "src-dailymed-interaction-amox-clav",
        },
        {
            "ingredient_a_id": "ing-pantoprazole",
            "ingredient_b_id": "ing-domperidone",
            "severity": "minor",
            "clinical_effect": "Complementary therapeutic combination; pantoprazole suppresses gastric acid secretion while domperidone accelerates gastric emptying, reducing reflux mucosal exposure.",
            "source_id": "src-cdsco-interaction-pantoprazole-domperidone",
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
        else:
            if exists.source_id != item["source_id"] or exists.clinical_effect != item["clinical_effect"]:
                exists.source_id = item["source_id"]
                exists.clinical_effect = item["clinical_effect"]
                exists.severity = item.get("severity", exists.severity)

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
