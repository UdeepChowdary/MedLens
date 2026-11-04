"use client";

import React, { useState, useEffect } from "react";
import { compareProducts, ComparisonResponse, ComparisonOutcome } from "@/lib/api";

interface MedicineItem {
  id: string;
  name: string;
  salt: string;
  strength: string;
  manufacturer: string;
  role: string;
  priceEstimate: string;
  genericAlternative: string;
  genericSavings: string;
  tags: string[];
}

interface DiseaseCategory {
  id: string;
  name: string;
  icon: string;
  category: string;
  description: string;
  commonSymptoms: string[];
  popularPair: [string, string];
  medicines: MedicineItem[];
}

const DISEASE_CATEGORIES: DiseaseCategory[] = [
  {
    id: "fever-pain",
    name: "Fever & Body Ache",
    icon: "🌡️",
    category: "Antipyretics & Analgesics",
    description: "Acute fever, headaches, body pain, viral pyrexia, and discomfort.",
    commonSymptoms: ["High body temperature (>99°F)", "Headache", "Body aches & joint stiffness", "Fatigue"],
    popularPair: ["dolo-650", "calpol-500"],
    medicines: [
      {
        id: "dolo-650",
        name: "Dolo 650",
        salt: "Paracetamol IP",
        strength: "650 mg",
        manufacturer: "Micro Labs Ltd",
        role: "High-strength antipyretic & analgesic for intense fever and adult aches",
        priceEstimate: "₹34 / 15 tabs",
        genericAlternative: "PMBJP Paracetamol 650",
        genericSavings: "75% savings (~₹8.50)",
        tags: ["High Strength", "Adult Fever", "Analgesic"],
      },
      {
        id: "calpol-500",
        name: "Calpol 500",
        salt: "Paracetamol IP",
        strength: "500 mg",
        manufacturer: "GlaxoSmithKline (GSK)",
        role: "Standard mild-to-moderate antipyretic with high gastric tolerance",
        priceEstimate: "₹22 / 15 tabs",
        genericAlternative: "PMBJP Paracetamol 500",
        genericSavings: "72% savings (~₹6.00)",
        tags: ["Standard Dose", "Mild Fever", "Gastric Safe"],
      },
      {
        id: "crocin-650",
        name: "Crocin 650",
        salt: "Paracetamol IP (Optizorb)",
        strength: "650 mg",
        manufacturer: "GlaxoSmithKline (GSK)",
        role: "Fast-dispersing paracetamol designed for rapid gastric dissolution",
        priceEstimate: "₹36 / 15 tabs",
        genericAlternative: "PMBJP Paracetamol 650",
        genericSavings: "76% savings (~₹8.50)",
        tags: ["Fast Release", "Rapid Relief", "Optizorb Tech"],
      },
      {
        id: "paracip-500",
        name: "Paracip 500",
        salt: "Paracetamol IP",
        strength: "500 mg",
        manufacturer: "Cipla Ltd",
        role: "Bioequivalent paracetamol formulation optimized for cost-effectiveness",
        priceEstimate: "₹16 / 10 tabs",
        genericAlternative: "PMBJP Paracetamol 500",
        genericSavings: "62% savings (~₹6.00)",
        tags: ["Affordable", "Bioequivalent", "Standard Care"],
      },
      {
        id: "combiflam",
        name: "Combiflam",
        salt: "Ibuprofen + Paracetamol",
        strength: "400 mg + 325 mg",
        manufacturer: "Sanofi India",
        role: "Dual-action NSAID + antipyretic for severe inflammatory body & muscular trauma",
        priceEstimate: "₹45 / 20 tabs",
        genericAlternative: "PMBJP Ibuprofen + Paracetamol",
        genericSavings: "73% savings (~₹12.00)",
        tags: ["Dual Action", "Anti-Inflammatory", "Muscular Pain"],
      },
    ],
  },
  {
    id: "acidity-gerd",
    name: "Acidity & Acid Reflux",
    icon: "🧪",
    category: "Proton Pump Inhibitors & Antacids",
    description: "Heartburn, gastroesophageal reflux (GERD), erosive esophagitis, and hyperacidity.",
    commonSymptoms: ["Chest burning / heartburn", "Sour acid regurgitation", "Post-meal bloating", "Stomach irritation"],
    popularPair: ["pan-40", "omez-20"],
    medicines: [
      {
        id: "pan-40",
        name: "Pan 40",
        salt: "Pantoprazole Sodium IP",
        strength: "40 mg",
        manufacturer: "Alkem Laboratories Ltd",
        role: "Irreversible PPI suppressing basal and stimulated gastric acid; low CYP2C19 interaction",
        priceEstimate: "₹155 / 15 tabs",
        genericAlternative: "PMBJP Pantoprazole 40",
        genericSavings: "87% savings (~₹20.00)",
        tags: ["Long-Acting", "Low Drug Interactions", "Once Daily Morning"],
      },
      {
        id: "omez-20",
        name: "Omez 20mg",
        salt: "Omeprazole IP",
        strength: "20 mg",
        manufacturer: "Dr. Reddy's Laboratories",
        role: "Fast-acting proton pump inhibitor for acute gastric hyperacidity and ulcer relief",
        priceEstimate: "₹65 / 15 tabs",
        genericAlternative: "PMBJP Omeprazole 20",
        genericSavings: "77% savings (~₹15.00)",
        tags: ["Rapid Action", "Ulcer Healing", "Gold Standard"],
      },
      {
        id: "pantodac-40",
        name: "Pantodac 40",
        salt: "Pantoprazole Sodium IP",
        strength: "40 mg",
        manufacturer: "Zydus Cadila",
        role: "Enteric-coated gastro-resistant formulation for sustained GERD maintenance",
        priceEstimate: "₹160 / 15 tabs",
        genericAlternative: "PMBJP Pantoprazole 40",
        genericSavings: "87% savings (~₹20.00)",
        tags: ["Enteric Coated", "Maintenance", "Reflux Control"],
      },
      {
        id: "pan-d",
        name: "Pan-D",
        salt: "Pantoprazole + Domperidone SR",
        strength: "40 mg + 30 mg",
        manufacturer: "Alkem Laboratories Ltd",
        role: "Dual acid suppression + prokinetic motility booster for reflux with nausea and fullness",
        priceEstimate: "₹195 / 15 tabs",
        genericAlternative: "PMBJP Pantoprazole + Domperidone",
        genericSavings: "82% savings (~₹35.00)",
        tags: ["Prokinetic Combo", "Anti-Nausea", "Sustained Release"],
      },
    ],
  },
  {
    id: "cold-allergies",
    name: "Cold, Cough & Allergies",
    icon: "🤧",
    category: "Antihistamines & Respiratory Care",
    description: "Runny nose, sneezing, seasonal allergic rhinitis, watery eyes, and bronchial cough.",
    commonSymptoms: ["Continuous sneezing", "Clear runny nose", "Throat scratchiness", "Itchy watery eyes"],
    popularPair: ["cetirizine-10", "montek-10"],
    medicines: [
      {
        id: "cetirizine-10",
        name: "Cetirizine 10mg",
        salt: "Cetirizine Hydrochloride",
        strength: "10 mg",
        manufacturer: "Cipla Ltd",
        role: "Rapid peripheral H1-antihistamine for acute allergic rhinitis and urticaria",
        priceEstimate: "₹25 / 10 tabs",
        genericAlternative: "PMBJP Cetirizine 10",
        genericSavings: "82% savings (~₹4.50)",
        tags: ["Fast Acting", "24-Hr Relief", "Affordable"],
      },
      {
        id: "montek-10",
        name: "Montek LC 10",
        salt: "Montelukast + Levocetirizine",
        strength: "10 mg + 5 mg",
        manufacturer: "Sun Pharma",
        role: "Synergistic leukotriene antagonist + antihistamine for chronic allergic cough & asthma",
        priceEstimate: "₹175 / 10 tabs",
        genericAlternative: "PMBJP Montelukast + Levocetirizine",
        genericSavings: "81% savings (~₹32.00)",
        tags: ["Dual Action", "Non-Sedating", "Allergic Asthma"],
      },
      {
        id: "montair-10",
        name: "Montair 10",
        salt: "Montelukast Sodium",
        strength: "10 mg",
        manufacturer: "Cipla Ltd",
        role: "Targeted leukotriene inhibitor preventing bronchospasm and night-time coughing",
        priceEstimate: "₹140 / 10 tabs",
        genericAlternative: "PMBJP Montelukast 10",
        genericSavings: "83% savings (~₹24.00)",
        tags: ["Bronchial Protection", "Night Symptoms", "Maintenance"],
      },
      {
        id: "benadryl-cough",
        name: "Benadryl Cough Formula",
        salt: "Diphenhydramine + Ammonium Chloride",
        strength: "Syrup Formulation",
        manufacturer: "Johnson & Johnson",
        role: "Centrally-acting antitussive soothing throat irritation and easing sleep during cold",
        priceEstimate: "₹125 / 100ml",
        genericAlternative: "PMBJP Cough Syrup Expectorant",
        genericSavings: "76% savings (~₹30.00)",
        tags: ["Cough Suppressant", "Sleep Aid", "Throat Coating"],
      },
    ],
  },
  {
    id: "infections-antibiotic",
    name: "Bacterial Infections",
    icon: "🦠",
    category: "Prescription Antibiotics (Schedule H)",
    description: "Bacterial respiratory infections, tonsillitis, dental abscesses, and urinary infections.",
    commonSymptoms: ["Bacterial fever", "Purulent throat exudate", "Dental inflammation", "Localized bacterial pain"],
    popularPair: ["augmentin-625", "azithral-500"],
    medicines: [
      {
        id: "augmentin-625",
        name: "Augmentin 625 Duo",
        salt: "Amoxicillin + Clavulanic Acid",
        strength: "500 mg + 125 mg",
        manufacturer: "GlaxoSmithKline (GSK)",
        role: "Gold-standard beta-lactamase protected broad-spectrum antibiotic for mixed bacterial pathogens",
        priceEstimate: "₹205 / 10 tabs",
        genericAlternative: "PMBJP Amoxy-Clav 625",
        genericSavings: "73% savings (~₹55.00)",
        tags: ["Broad Spectrum", "Dental/ENT", "Beta-Lactamase Resistant"],
      },
      {
        id: "azithral-500",
        name: "Azithral 500",
        salt: "Azithromycin IP",
        strength: "500 mg",
        manufacturer: "Alembic Pharmaceuticals",
        role: "Convenient once-daily 3-day macrolide antibiotic with high intracellular lung tissue accumulation",
        priceEstimate: "₹135 / 5 tabs",
        genericAlternative: "PMBJP Azithromycin 500",
        genericSavings: "72% savings (~₹38.00)",
        tags: ["Once Daily", "3-Day Regimen", "Respiratory & Throat"],
      },
      {
        id: "zithromax-500",
        name: "Zithromax 500mg",
        salt: "Azithromycin",
        strength: "500 mg",
        manufacturer: "Pfizer",
        role: "Global reference standard macrolide antibiotic for atypical and community-acquired pneumonia",
        priceEstimate: "₹160 / 5 tabs",
        genericAlternative: "PMBJP Azithromycin 500",
        genericSavings: "76% savings (~₹38.00)",
        tags: ["Global Reference", "Chest Infections", "Convenient"],
      },
      {
        id: "azee-500",
        name: "Azee 500",
        salt: "Azithromycin IP",
        strength: "500 mg",
        manufacturer: "Cipla Ltd",
        role: "Widely available bioequivalent macrolide antibiotic for upper and lower respiratory tracts",
        priceEstimate: "₹125 / 5 tabs",
        genericAlternative: "PMBJP Azithromycin 500",
        genericSavings: "70% savings (~₹38.00)",
        tags: ["Bioequivalent", "ENT Infections", "Schedule H"],
      },
    ],
  },
  {
    id: "hypertension-heart",
    name: "High Blood Pressure & Heart",
    icon: "❤️",
    category: "Antihypertensives & Cardioprotective",
    description: "Essential hypertension, arterial pressure management, lipid balance, and arterial health.",
    commonSymptoms: ["Elevated systolic/diastolic BP (>130/80)", "Mild morning headache", "Fatigue", "Cardiovascular risk"],
    popularPair: ["losartan-50", "amlodac-5"],
    medicines: [
      {
        id: "losartan-50",
        name: "Losartan 50",
        salt: "Losartan Potassium IP",
        strength: "50 mg",
        manufacturer: "Cipla Ltd",
        role: "Angiotensin receptor blocker (ARB) reducing peripheral resistance while preserving renal function",
        priceEstimate: "₹65 / 15 tabs",
        genericAlternative: "PMBJP Losartan 50",
        genericSavings: "78% savings (~₹14.00)",
        tags: ["Renal Protective", "No Cough", "First-Line ARB"],
      },
      {
        id: "amlodac-5",
        name: "Amlodac 5",
        salt: "Amlodipine Besylate IP",
        strength: "5 mg",
        manufacturer: "Zydus Cadila",
        role: "Long-acting dihydropyridine calcium channel blocker promoting smooth muscle vasodilation",
        priceEstimate: "₹45 / 15 tabs",
        genericAlternative: "PMBJP Amlodipine 5",
        genericSavings: "82% savings (~₹8.00)",
        tags: ["24-Hr Control", "Calcium Blocker", "Vasodilator"],
      },
      {
        id: "ecosprin-75",
        name: "Ecosprin 75",
        salt: "Aspirin IP (Gastro-resistant)",
        strength: "75 mg",
        manufacturer: "USV Ltd",
        role: "Low-dose antiplatelet therapy for primary and secondary cardiovascular event prevention",
        priceEstimate: "₹10 / 14 tabs",
        genericAlternative: "PMBJP Aspirin 75",
        genericSavings: "65% savings (~₹3.50)",
        tags: ["Cardioprotective", "Antiplatelet", "Enteric Coated"],
      },
      {
        id: "lipitor-10",
        name: "Lipitor 10mg",
        salt: "Atorvastatin Calcium",
        strength: "10 mg",
        manufacturer: "Pfizer",
        role: "HMG-CoA reductase inhibitor lowering atherogenic LDL-cholesterol and stabilizing plaque",
        priceEstimate: "₹110 / 10 tabs",
        genericAlternative: "PMBJP Atorvastatin 10",
        genericSavings: "84% savings (~₹18.00)",
        tags: ["Lipid Lowering", "LDL Reduction", "Global Standard"],
      },
      {
        id: "storvas-20",
        name: "Storvas 20",
        salt: "Atorvastatin IP",
        strength: "20 mg",
        manufacturer: "Sun Pharma",
        role: "High-potency statin formulation for intensive dyslipidemia and post-cardiac event therapy",
        priceEstimate: "₹180 / 15 tabs",
        genericAlternative: "PMBJP Atorvastatin 20",
        genericSavings: "84% savings (~₹28.00)",
        tags: ["High Potency", "Statin Therapy", "Cardiovascular"],
      },
    ],
  },
  {
    id: "diabetes-type2",
    name: "Diabetes Type 2",
    icon: "🩺",
    category: "Oral Hypoglycemic Agents",
    description: "Elevated fasting blood sugar, insulin resistance, HbA1c elevation, and glycemic stabilization.",
    commonSymptoms: ["Frequent urination", "Excessive thirst", "Fatigue", "Elevated HbA1c (>6.5%)"],
    popularPair: ["glycomet-500", "glucophage-500"],
    medicines: [
      {
        id: "glycomet-500",
        name: "Glycomet 500",
        salt: "Metformin Hydrochloride IP",
        strength: "500 mg",
        manufacturer: "USV Ltd",
        role: "First-line biguanide reducing hepatic glucose production and improving peripheral insulin uptake",
        priceEstimate: "₹28 / 20 tabs",
        genericAlternative: "PMBJP Metformin 500",
        genericSavings: "71% savings (~₹8.00)",
        tags: ["First-Line", "Weight Neutral", "Low Hypoglycemia Risk"],
      },
      {
        id: "glucophage-500",
        name: "Glucophage 500mg",
        salt: "Metformin Hydrochloride",
        strength: "500 mg",
        manufacturer: "Sun Pharma / Merck",
        role: "Global reference standard metformin formulation with superior gastro-intestinal tolerability",
        priceEstimate: "₹42 / 15 tabs",
        genericAlternative: "PMBJP Metformin 500",
        genericSavings: "81% savings (~₹8.00)",
        tags: ["Reference Brand", "Cardioprotective", "Proven Long-Term"],
      },
      {
        id: "glucophage-1000",
        name: "Glucophage 1000mg",
        salt: "Metformin Hydrochloride",
        strength: "1000 mg",
        manufacturer: "Sun Pharma / Merck",
        role: "Higher-strength single-tablet metformin for patients requiring intensified daily glycemic control",
        priceEstimate: "₹75 / 15 tabs",
        genericAlternative: "PMBJP Metformin 1000",
        genericSavings: "80% savings (~₹15.00)",
        tags: ["High Dose", "Convenient Once/Twice", "Targeted HbA1c"],
      },
    ],
  },
  {
    id: "inflammation-joint",
    name: "Muscle, Joint & Dental Pain",
    icon: "⚡",
    category: "Non-Steroidal Anti-Inflammatory Drugs (NSAIDs)",
    description: "Musculoskeletal trauma, arthritis flare-ups, sports injuries, sprains, and dental inflammation.",
    commonSymptoms: ["Joint swelling & warmth", "Localized muscle tenderness", "Throbbing dental ache", "Post-injury inflammation"],
    popularPair: ["brufen-400", "combiflam"],
    medicines: [
      {
        id: "brufen-400",
        name: "Brufen 400",
        salt: "Ibuprofen IP",
        strength: "400 mg",
        manufacturer: "Abbott Healthcare",
        role: "Potent COX-1/COX-2 inhibitor directly reducing tissue inflammation, swelling, and musculoskeletal pain",
        priceEstimate: "₹24 / 15 tabs",
        genericAlternative: "PMBJP Ibuprofen 400",
        genericSavings: "73% savings (~₹6.50)",
        tags: ["Pure NSAID", "Anti-Inflammatory", "Joint Relief"],
      },
      {
        id: "combiflam",
        name: "Combiflam",
        salt: "Ibuprofen + Paracetamol",
        strength: "400 mg + 325 mg",
        manufacturer: "Sanofi India",
        role: "Combined analgesic-antipyretic with NSAID for synergistic relief of toothaches and acute sprains",
        priceEstimate: "₹45 / 20 tabs",
        genericAlternative: "PMBJP Ibuprofen + Paracetamol",
        genericSavings: "73% savings (~₹12.00)",
        tags: ["Synergistic", "Rapid Relief", "Dental/Trauma"],
      },
      {
        id: "paracip-500",
        name: "Paracip 500",
        salt: "Paracetamol IP",
        strength: "500 mg",
        manufacturer: "Cipla Ltd",
        role: "Gastric-sparing central analgesic; ideal when NSAIDs like Ibuprofen are contraindicated (e.g. ulcers)",
        priceEstimate: "₹16 / 10 tabs",
        genericAlternative: "PMBJP Paracetamol 500",
        genericSavings: "62% savings (~₹6.00)",
        tags: ["Gastric Safe", "No Bleeding Risk", "Ulcer Friendly"],
      },
    ],
  },
  {
    id: "nausea-vomiting",
    name: "Nausea & Motion Sickness",
    icon: "🤢",
    category: "Antiemetics & Prokinetics",
    description: "Acute nausea, vomiting, dizziness, travel sickness, and post-operative or reflux-related emesis.",
    commonSymptoms: ["Queasiness & vomiting", "Travel dizziness", "Acid regurgitation fullness", "Stomach sluggishness"],
    popularPair: ["vomistop-10", "pan-d"],
    medicines: [
      {
        id: "vomistop-10",
        name: "Vomistop 10",
        salt: "Domperidone IP",
        strength: "10 mg",
        manufacturer: "Meyer Organics",
        role: "Peripheral D2-receptor antagonist increasing upper GI motility without crossing blood-brain barrier",
        priceEstimate: "₹38 / 10 tabs",
        genericAlternative: "PMBJP Domperidone 10",
        genericSavings: "79% savings (~₹8.00)",
        tags: ["Prokinetic", "Minimal Drowsiness", "Gastric Emptying"],
      },
      {
        id: "pan-d",
        name: "Pan-D",
        salt: "Pantoprazole + Domperidone SR",
        strength: "40 mg + 30 mg",
        manufacturer: "Alkem Laboratories Ltd",
        role: "Combines sustained-release anti-emetic prokinetic with pantoprazole for gastric acid suppression",
        priceEstimate: "₹195 / 15 tabs",
        genericAlternative: "PMBJP Pantoprazole + Domperidone",
        genericSavings: "82% savings (~₹35.00)",
        tags: ["Dual Relief", "GERD Nausea", "Sustained Release"],
      },
    ],
  },
];

function resultBadgeStyle(result: ComparisonOutcome): React.CSSProperties {
  switch (result) {
    case "match":
      return { backgroundColor: "#dcfce7", color: "#16a34a", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    case "difference":
      return { backgroundColor: "#fffbeb", color: "#d97706", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    case "conflict":
      return { backgroundColor: "#fee2e2", color: "#dc2626", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    default:
      return { backgroundColor: "#f1f5f9", color: "#94a3b8", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
  }
}

export default function CompareByDiseasePage() {
  const [selectedDiseaseId, setSelectedDiseaseId] = useState<string>("fever-pain");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [brandA, setBrandA] = useState<string>("dolo-650");
  const [brandB, setBrandB] = useState<string>("calpol-500");

  const [isComparing, setIsComparing] = useState(false);
  const [compareResult, setCompareResult] = useState<ComparisonResponse | null>(null);
  const [compareError, setCompareError] = useState<string | null>(null);

  // User Profile Allergies for safety checks
  const [userAllergies, setUserAllergies] = useState<string[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("medlens_user_allergies");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) setUserAllergies(parsed);
      }
    } catch {
      // Ignore
    }
  }, []);

  const currentDisease = DISEASE_CATEGORIES.find((d) => d.id === selectedDiseaseId) || DISEASE_CATEGORIES[0];

  // When disease changes, set popular pair
  const handleSelectDisease = (disease: DiseaseCategory) => {
    setSelectedDiseaseId(disease.id);
    setBrandA(disease.popularPair[0]);
    setBrandB(disease.popularPair[1]);
    setCompareResult(null);
    setCompareError(null);
  };

  const handleSelectMedicineSlot = (medId: string, slot: "A" | "B") => {
    if (slot === "A") {
      setBrandA(medId);
      if (brandB === medId) {
        // Automatically swap with another medicine in this category if same
        const other = currentDisease.medicines.find((m) => m.id !== medId);
        if (other) setBrandB(other.id);
      }
    } else {
      setBrandB(medId);
      if (brandA === medId) {
        const other = currentDisease.medicines.find((m) => m.id !== medId);
        if (other) setBrandA(other.id);
      }
    }
    setCompareResult(null);
  };

  // Find medicine items across all categories
  const allMedicines = DISEASE_CATEGORIES.flatMap((d) => d.medicines);
  const medItemA = allMedicines.find((m) => m.id === brandA) || currentDisease.medicines[0];
  const medItemB = allMedicines.find((m) => m.id === brandB) || currentDisease.medicines[1];

  const handleCompare = async () => {
    setIsComparing(true);
    setCompareResult(null);
    setCompareError(null);

    const { data, error } = await compareProducts(brandA, brandB);

    if (error) {
      setCompareError(error.message);
      setIsComparing(false);
      return;
    }

    if (data) {
      setCompareResult(data);
    }
    setIsComparing(false);
  };

  // Filter diseases based on search
  const filteredDiseases = DISEASE_CATEGORIES.filter((d) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      d.name.toLowerCase().includes(q) ||
      d.description.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q) ||
      d.commonSymptoms.some((s) => s.toLowerCase().includes(q)) ||
      d.medicines.some((m) => m.name.toLowerCase().includes(q) || m.salt.toLowerCase().includes(q))
    );
  });

  // Check if medicine conflicts with user allergies
  const checkAllergyConflict = (saltText: string) => {
    if (userAllergies.length === 0) return null;
    const saltLower = saltText.toLowerCase();
    for (const allergy of userAllergies) {
      const alLower = allergy.toLowerCase().trim();
      if (!alLower) continue;
      if (saltLower.includes(alLower) || alLower.includes(saltLower)) {
        return allergy;
      }
    }
    return null;
  };

  return (
    <div style={{ padding: "32px", maxWidth: "1100px", margin: "0 auto" }}>
      {/* Page Header */}
      <div style={{ marginBottom: "28px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
          Compare Medicines by Health Condition
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "15px", lineHeight: "1.6" }}>
          Select a medical condition or symptom to explore clinically relevant treatments, compare formulations
          side-by-side, analyze active salts, and discover cost-saving generic alternatives.
        </p>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: "28px" }}>
        <div style={{ position: "relative", maxWidth: "600px" }}>
          <input
            type="text"
            placeholder="Search symptoms (e.g. fever, headache, acidity, asthma, infection)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "12px 18px 12px 42px",
              borderRadius: "10px",
              border: "1px solid var(--border)",
              fontSize: "14.5px",
              outline: "none",
              backgroundColor: "white",
              boxShadow: "0 1px 3px rgba(0,0,0,0.03)"
            }}
          />
          <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)", fontSize: "18px" }}>
            🔍
          </span>
        </div>
      </div>

      {/* STEP 1: Condition Selector */}
      <div style={{ marginBottom: "32px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <span style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            backgroundColor: "var(--blue)",
            color: "white",
            fontWeight: "bold",
            fontSize: "14px"
          }}>
            1
          </span>
          <h2 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
            Select Medical Condition / Health Concern
          </h2>
        </div>

        {/* Condition Cards Grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
          gap: "14px"
        }}>
          {filteredDiseases.map((disease) => {
            const isSelected = disease.id === selectedDiseaseId;
            return (
              <button
                key={disease.id}
                type="button"
                onClick={() => handleSelectDisease(disease)}
                style={{
                  textAlign: "left",
                  padding: "18px",
                  borderRadius: "14px",
                  backgroundColor: isSelected ? "#eff6ff" : "white",
                  border: isSelected ? "2px solid var(--blue)" : "1px solid var(--border)",
                  boxShadow: isSelected ? "0 4px 12px rgba(37,99,235,0.12)" : "0 1px 3px rgba(0,0,0,0.03)",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  display: "flex",
                  flexDirection: "column",
                  gap: "8px"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "28px" }}>{disease.icon}</span>
                  {isSelected && (
                    <span style={{
                      fontSize: "11px",
                      fontWeight: 700,
                      backgroundColor: "var(--blue)",
                      color: "white",
                      padding: "2px 8px",
                      borderRadius: "10px"
                    }}>
                      SELECTED
                    </span>
                  )}
                </div>
                <div>
                  <h3 style={{ fontSize: "15.5px", fontWeight: 700, color: isSelected ? "var(--blue)" : "var(--text-primary)", margin: "0 0 4px 0" }}>
                    {disease.name}
                  </h3>
                  <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0, lineHeight: "1.4" }}>
                    {disease.description}
                  </p>
                </div>
                <div style={{ marginTop: "auto", paddingTop: "6px", fontSize: "11.5px", color: "#64748b", fontWeight: 500 }}>
                  {disease.medicines.length} Relevant Medicines
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* STEP 2: Relevant Medicines for Selected Condition */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "32px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "20px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
              <span style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                backgroundColor: "var(--blue)",
                color: "white",
                fontWeight: "bold",
                fontSize: "14px"
              }}>
                2
              </span>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                Relevant Medicines for: {currentDisease.name}
              </h2>
            </div>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
              Choose which two medicines you want to compare in Slot A and Slot B below.
            </p>
          </div>

          {/* Quick preset popular pair button */}
          <button
            type="button"
            onClick={() => {
              setBrandA(currentDisease.popularPair[0]);
              setBrandB(currentDisease.popularPair[1]);
              setCompareResult(null);
            }}
            style={{
              padding: "7px 14px",
              borderRadius: "8px",
              border: "1px solid #bfdbfe",
              backgroundColor: "#eff6ff",
              color: "var(--blue)",
              fontSize: "12.5px",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            ⚡ Load Popular Pair ({currentDisease.medicines.find((m) => m.id === currentDisease.popularPair[0])?.name} vs {currentDisease.medicines.find((m) => m.id === currentDisease.popularPair[1])?.name})
          </button>
        </div>

        {/* Medicine Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(290px, 1fr))", gap: "16px" }}>
          {currentDisease.medicines.map((med) => {
            const isSlotA = brandA === med.id;
            const isSlotB = brandB === med.id;
            const allergyConflict = checkAllergyConflict(med.salt);

            return (
              <div
                key={med.id}
                style={{
                  border: isSlotA || isSlotB ? "2px solid var(--blue)" : "1px solid var(--border)",
                  borderRadius: "12px",
                  padding: "18px",
                  backgroundColor: isSlotA ? "#f0f7ff" : isSlotB ? "#faf5ff" : "#f8fafc",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  position: "relative"
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                    <div>
                      <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                        {med.name}
                      </h3>
                      <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {med.manufacturer}
                      </span>
                    </div>

                    {/* Slot Indicator Pills */}
                    {isSlotA && (
                      <span style={{ backgroundColor: "var(--blue)", color: "white", padding: "2px 8px", borderRadius: "6px", fontSize: "11px", fontWeight: 700 }}>
                        SLOT A
                      </span>
                    )}
                    {isSlotB && (
                      <span style={{ backgroundColor: "#7c3aed", color: "white", padding: "2px 8px", borderRadius: "6px", fontSize: "11px", fontWeight: 700 }}>
                        SLOT B
                      </span>
                    )}
                  </div>

                  {/* Active Salt & Strength */}
                  <div style={{ marginBottom: "10px" }}>
                    <span style={{
                      display: "inline-block",
                      fontSize: "12.5px",
                      fontWeight: 600,
                      padding: "3px 8px",
                      borderRadius: "6px",
                      backgroundColor: "#e2e8f0",
                      color: "#334155"
                    }}>
                      {med.salt} ({med.strength})
                    </span>
                  </div>

                  {/* Allergy Conflict Warning (if matching user profile) */}
                  {allergyConflict && (
                    <div style={{
                      marginBottom: "10px",
                      padding: "6px 10px",
                      borderRadius: "6px",
                      backgroundColor: "#fee2e2",
                      color: "#b91c1c",
                      fontSize: "11.5px",
                      fontWeight: 600,
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}>
                      <span>⚠</span>
                      <span>Matches your documented &ldquo;{allergyConflict}&rdquo; allergy!</span>
                    </div>
                  )}

                  {/* Clinical Role */}
                  <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: "1.4", margin: "0 0 12px 0" }}>
                    {med.role}
                  </p>

                  {/* Generic Alternative & Savings */}
                  <div style={{
                    backgroundColor: "white",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    marginBottom: "14px",
                    fontSize: "11.5px"
                  }}>
                    <div style={{ color: "#166534", fontWeight: 600, display: "flex", justifyContent: "space-between" }}>
                      <span>Jan Aushadhi Alternative:</span>
                      <span>{med.genericSavings}</span>
                    </div>
                    <div style={{ color: "var(--text-secondary)", marginTop: "2px" }}>
                      {med.genericAlternative} vs {med.priceEstimate}
                    </div>
                  </div>
                </div>

                {/* Selection Action Buttons */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                  <button
                    type="button"
                    onClick={() => handleSelectMedicineSlot(med.id, "A")}
                    style={{
                      padding: "6px 10px",
                      borderRadius: "6px",
                      border: isSlotA ? "1px solid var(--blue)" : "1px solid var(--border)",
                      backgroundColor: isSlotA ? "var(--blue)" : "white",
                      color: isSlotA ? "white" : "var(--text-primary)",
                      fontSize: "12px",
                      fontWeight: 600,
                      cursor: "pointer"
                    }}
                  >
                    {isSlotA ? "✓ In Slot A" : "Set as Medicine A"}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSelectMedicineSlot(med.id, "B")}
                    style={{
                      padding: "6px 10px",
                      borderRadius: "6px",
                      border: isSlotB ? "1px solid #7c3aed" : "1px solid var(--border)",
                      backgroundColor: isSlotB ? "#7c3aed" : "white",
                      color: isSlotB ? "white" : "var(--text-primary)",
                      fontSize: "12px",
                      fontWeight: 600,
                      cursor: "pointer"
                    }}
                  >
                    {isSlotB ? "✓ In Slot B" : "Set as Medicine B"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* STEP 3: Side-by-Side Comparison Workspace */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "32px",
        marginBottom: "32px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "24px" }}>
          <span style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            backgroundColor: "var(--blue)",
            color: "white",
            fontWeight: "bold",
            fontSize: "14px"
          }}>
            3
          </span>
          <h2 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
            Side-by-Side Comparison Workspace
          </h2>
        </div>

        {/* Comparison Trays */}
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "20px", justifyContent: "center" }}>
          {/* Medicine A Card */}
          <div style={{
            flex: "1 1 300px",
            backgroundColor: "#f0f7ff",
            border: "2px solid #93c5fd",
            borderRadius: "12px",
            padding: "20px"
          }}>
            <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--blue)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>
              Medicine A
            </div>
            <h3 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", margin: "0 0 4px 0" }}>
              {medItemA.name}
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "0 0 10px 0" }}>
              {medItemA.manufacturer}
            </p>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "#1e3a8a", backgroundColor: "white", padding: "6px 10px", borderRadius: "6px", display: "inline-block" }}>
              {medItemA.salt} ({medItemA.strength})
            </div>
          </div>

          {/* VS Divider */}
          <div style={{
            width: "44px",
            height: "44px",
            borderRadius: "50%",
            backgroundColor: "var(--blue)",
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: "bold",
            fontSize: "15px",
            boxShadow: "0 2px 6px rgba(37,99,235,0.3)"
          }}>
            VS
          </div>

          {/* Medicine B Card */}
          <div style={{
            flex: "1 1 300px",
            backgroundColor: "#faf5ff",
            border: "2px solid #d8b4fe",
            borderRadius: "12px",
            padding: "20px"
          }}>
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#7c3aed", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>
              Medicine B
            </div>
            <h3 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", margin: "0 0 4px 0" }}>
              {medItemB.name}
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "0 0 10px 0" }}>
              {medItemB.manufacturer}
            </p>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "#581c87", backgroundColor: "white", padding: "6px 10px", borderRadius: "6px", display: "inline-block" }}>
              {medItemB.salt} ({medItemB.strength})
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div style={{ display: "flex", justifyContent: "center", marginTop: "28px" }}>
          <button
            className="btn-primary"
            onClick={handleCompare}
            disabled={isComparing || brandA === brandB}
            style={{
              padding: "14px 36px",
              fontSize: "15.5px",
              fontWeight: 700,
              opacity: isComparing || brandA === brandB ? 0.7 : 1,
              boxShadow: "0 4px 14px rgba(37,99,235,0.25)"
            }}
          >
            {isComparing ? "Analyzing Formulations..." : `Compare ${medItemA.name} vs ${medItemB.name}`}
          </button>
        </div>

        {brandA === brandB && (
          <p style={{ textAlign: "center", color: "#dc2626", fontSize: "13px", marginTop: "10px" }}>
            Please select two different medicines to perform a side-by-side comparison.
          </p>
        )}
      </div>

      {/* Loading Spinner */}
      {isComparing && (
        <div style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ width: "48px", height: "48px", borderRadius: "50%", border: "3px solid var(--blue)", borderTopColor: "transparent", margin: "0 auto 16px", animation: "spin 0.8s linear infinite" }} />
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Comparing composition, active salts, and bioequivalence...</p>
        </div>
      )}

      {/* Error State */}
      {!isComparing && compareError && (
        <div style={{ backgroundColor: "#fee2e2", borderLeft: "4px solid #ef4444", padding: "16px 20px", borderRadius: "8px", marginBottom: "24px" }}>
          <strong style={{ color: "#dc2626" }}>Comparison Error:</strong>
          <span style={{ color: "#dc2626", marginLeft: "8px" }}>{compareError}</span>
        </div>
      )}

      {/* Delta Matrix Results */}
      {!isComparing && compareResult && (
        <div style={{ animation: "fade-up 0.5s ease-out" }}>
          {/* Key Clinical Differences Highlight Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "24px" }}>
            {/* Strength Delta Card */}
            <div style={{
              backgroundColor: compareResult.strength_delta?.difference_detected ? "#fffbeb" : "#ecfdf5",
              border: `1px solid ${compareResult.strength_delta?.difference_detected ? "#fcd34d" : "#a7f3d0"}`,
              padding: "20px",
              borderRadius: "12px"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span>{compareResult.strength_delta?.difference_detected ? "⚖️" : "✓"}</span>
                <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                  Active Strength Comparison
                </h4>
              </div>
              <p style={{ fontSize: "13.5px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
                {compareResult.strength_delta?.warning || "Both medicines deliver bioequivalent or identical active therapeutic strength."}
                {compareResult.strength_delta?.numeric_delta !== undefined && (
                  <span style={{ fontWeight: 700, color: "var(--text-primary)" }}> (Difference: {compareResult.strength_delta.numeric_delta} {compareResult.strength_delta.unit ?? ""})</span>
                )}
              </p>
            </div>

            {/* Therapeutic Equivalence */}
            <div style={{
              backgroundColor: "#eff6ff",
              border: "1px solid #bfdbfe",
              padding: "20px",
              borderRadius: "12px"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span>🔬</span>
                <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                  Therapeutic Equivalence
                </h4>
              </div>
              <p style={{ fontSize: "13.5px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
                <strong>{compareResult.therapeutic_equivalence?.status}:</strong> {compareResult.therapeutic_equivalence?.note}
              </p>
            </div>
          </div>

          {/* Pricing & Jan Aushadhi Generic Savings Comparison */}
          <div style={{
            backgroundColor: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: "12px",
            padding: "20px",
            marginBottom: "24px"
          }}>
            <h4 style={{ fontSize: "16px", fontWeight: 700, color: "#166534", margin: "0 0 12px 0", display: "flex", alignItems: "center", gap: "8px" }}>
              <span>💰</span>
              <span>Cost & Generic Jan Aushadhi Savings Comparison</span>
            </h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ backgroundColor: "white", padding: "14px", borderRadius: "8px", border: "1px solid #dcfce7" }}>
                <div style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: "14px" }}>{medItemA.name}</div>
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>Est. Price: {medItemA.priceEstimate}</div>
                <div style={{ fontSize: "12px", color: "#15803d", fontWeight: 600, marginTop: "4px" }}>
                  Generic: {medItemA.genericAlternative} ({medItemA.genericSavings})
                </div>
              </div>

              <div style={{ backgroundColor: "white", padding: "14px", borderRadius: "8px", border: "1px solid #dcfce7" }}>
                <div style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: "14px" }}>{medItemB.name}</div>
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>Est. Price: {medItemB.priceEstimate}</div>
                <div style={{ fontSize: "12px", color: "#15803d", fontWeight: 600, marginTop: "4px" }}>
                  Generic: {medItemB.genericAlternative} ({medItemB.genericSavings})
                </div>
              </div>
            </div>
          </div>

          {/* Composition Delta Matrix Table */}
          {compareResult.attributes.length > 0 && (
            <div style={{ backgroundColor: "white", borderRadius: "16px", border: "1px solid var(--border)", overflow: "hidden", marginBottom: "24px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr", backgroundColor: "var(--surface-alt)", borderBottom: "1px solid var(--border)" }}>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-secondary)", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Clinical Attribute
                </div>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                  {medItemA.name}
                </div>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                  {medItemB.name}
                </div>
              </div>

              {compareResult.attributes.map((attr, i) => (
                <div key={i} style={{
                  display: "grid",
                  gridTemplateColumns: "1.5fr 1fr 1fr",
                  borderBottom: i !== compareResult.attributes.length - 1 ? "1px solid var(--border)" : "none",
                  backgroundColor: attr.result === "difference" || attr.result === "conflict" ? "#fffbeb" : "transparent"
                }}>
                  <div style={{ padding: "16px" }}>
                    <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>{attr.field}</div>
                    {attr.reason && <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{attr.reason}</div>}
                  </div>
                  <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center" }}>
                    <span style={resultBadgeStyle(attr.result)}>{attr.result}</span>
                  </div>
                  <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center", fontSize: "13px", color: "var(--text-secondary)" }}>
                    {attr.evidence.join("; ") || "Verified monograph standard"}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Excipient Differences */}
          {compareResult.excipient_differences.length > 0 && (
            <div style={{ backgroundColor: "white", borderRadius: "12px", border: "1px solid var(--border)", padding: "20px", marginBottom: "24px" }}>
              <h4 style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "12px", fontSize: "16px" }}>
                Excipient / Inactive Formulation Differences
              </h4>
              <ul style={{ paddingLeft: "20px", margin: 0, color: "var(--text-secondary)", fontSize: "14px", display: "flex", flexDirection: "column", gap: "6px" }}>
                {compareResult.excipient_differences.map((diff, i) => <li key={i}>{diff}</li>)}
              </ul>
            </div>
          )}

          {/* Clinical Limitations */}
          {compareResult.limitations.length > 0 && (
            <div style={{ backgroundColor: "var(--surface-alt)", borderRadius: "12px", padding: "16px 20px" }}>
              <h4 style={{ fontWeight: 600, color: "var(--text-muted)", marginBottom: "8px", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Clinical Limitations & Disclaimer
              </h4>
              <ul style={{ paddingLeft: "20px", margin: 0, color: "var(--text-secondary)", fontSize: "12.5px", display: "flex", flexDirection: "column", gap: "4px" }}>
                {compareResult.limitations.map((l, i) => <li key={i}>{l}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
