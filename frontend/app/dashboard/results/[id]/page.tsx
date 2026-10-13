"use client";

import React from "react";
import Link from "next/link";
import ProductOverview from "@/components/report/ProductOverview";
import IngredientCard from "@/components/report/IngredientCard";
import ExcipientCollapse from "@/components/report/ExcipientCollapse";
import SafetyModule from "@/components/report/SafetyModule";
import { ScrollReveal } from "@/components/ScrollReveal";
import { IcoArrow } from "@/components/Icons";

// --- MOCK DATA ---
const mockReport = {
  scan_id: "demo-scan",
  processing_time_ms: 2450,
  confidence_overall: 0.95,
  product: {
    detected_name: "Dolo 650",
    dosage_form: "Tablet",
    manufacturer: "Micro Labs Ltd",
    is_verified: true,
  },
  active_ingredients: [
    {
      canonical_name: "Paracetamol (Acetaminophen)",
      raw_label_text: "Paracetamol IP",
      strength: "650",
      numeric_value: 650,
      unit: "mg",
      role: "active",
      confidence: 0.98,
      explanation: "An analgesic and antipyretic agent that reduces pain signals in the nervous system and lowers body temperature by acting on the hypothalamus.",
      therapeutic_purpose: "To relieve mild to moderate pain and reduce fever.",
      evidence_sources: [
        { name: "OpenFDA", url: "https://open.fda.gov/" },
        { name: "National Library of Medicine", url: "https://pubchem.ncbi.nlm.nih.gov/compound/1983" }
      ]
    }
  ],
  inactive_ingredients: [
    { name: "Maize Starch", purpose: "Binder and disintegrant to help the tablet hold together and break apart in the stomach." },
    { name: "Povidone K30", purpose: "Binding agent." },
    { name: "Magnesium Stearate", purpose: "Lubricant to prevent ingredients from sticking to manufacturing equipment." }
  ],
  safety_profile: {
    purpose_summary: "Used for symptomatic relief of fever and pain. Should not be used continuously without medical supervision.",
    precautions: [
      "Do not exceed the maximum daily dose of 4000mg to avoid liver damage.",
      "Avoid consuming alcohol while taking this medication as it increases the risk of hepatotoxicity.",
      "Consult a doctor if symptoms persist for more than 3 days."
    ],
    contraindications: [
      "Known hypersensitivity to paracetamol.",
      "Severe hepatic impairment or active liver disease."
    ],
    adverse_effects: [
      "Nausea",
      "Skin rash",
      "Liver toxicity (in overdose)"
    ]
  },
  audit_hash: "a2b4c6d8e0f1g3h5i7j9k2l4m6n8o0p1q3r5s7t9u1v3w5x7y9z0"
};

export default function ResultsPage() {
  const [sourceImage, setSourceImage] = React.useState<string | null>(null);

  React.useEffect(() => {
    const savedImage = sessionStorage.getItem("scanned_image");
    if (savedImage) {
      requestAnimationFrame(() => {
        setSourceImage(savedImage);
      });
    }
  }, []);

  return (
    <div style={{ minHeight: "100%", backgroundColor: "var(--surface)", display: "flex", flexDirection: "column" }} className="font-sans">
      
      <div style={{ flex: 1, paddingTop: "32px", paddingBottom: "96px", paddingLeft: "24px", paddingRight: "24px", position: "relative" }}>
        <div style={{ maxWidth: "896px", margin: "0 auto" }}>
          
          <ScrollReveal variant="fade-up">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }} className="print-hide">
              <Link href="/dashboard/scan" style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--blue)", fontWeight: 500, textDecoration: "none" }}>
                <span style={{ transform: "rotate(180deg)", display: "flex" }}><IcoArrow /></span>
                Back to Scanner
              </Link>
              
              <button 
                onClick={() => window.print()}
                style={{ 
                  display: "inline-flex", alignItems: "center", gap: "8px", 
                  backgroundColor: "white", color: "var(--text-primary)", 
                  padding: "8px 16px", borderRadius: "8px", 
                  border: "1px solid var(--border)", fontWeight: 600, 
                  fontSize: "14px", cursor: "pointer",
                  boxShadow: "var(--shadow-sm)"
                }}
                className="hover:bg-slate-50 transition-colors"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Export PDF
              </button>
            </div>
          </ScrollReveal>

          {/* Uploaded Image Preview */}
          <ScrollReveal variant="fade-up" delay={50}>
            <div style={{ marginBottom: "24px", width: "100%", height: "220px", borderRadius: "16px", overflow: "hidden", position: "relative", backgroundColor: "#f1f5f9", border: "1px solid var(--border)" }}>
              <img 
                src={sourceImage || "/placeholder-med.svg"} 
                alt="Scanned Medicine Preview" 
                style={{ width: "100%", height: "100%", objectFit: "cover" }} 
              />
              <div style={{ position: "absolute", bottom: "16px", right: "16px", backgroundColor: "rgba(0,0,0,0.6)", color: "white", padding: "4px 10px", borderRadius: "8px", fontSize: "12px", fontWeight: 600, backdropFilter: "blur(4px)", display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4ade80" }}></span>
                Source Image
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal variant="fade-up" delay={100}>
            <div style={{ marginBottom: "32px" }}>
              <ProductOverview 
                name={mockReport.product.detected_name}
                manufacturer={mockReport.product.manufacturer}
                dosageForm={mockReport.product.dosage_form}
                confidence={mockReport.confidence_overall}
              />
            </div>
          </ScrollReveal>

          <ScrollReveal variant="fade-up" delay={200}>
            <h2 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "16px" }}>Active Ingredients</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "32px" }}>
              {mockReport.active_ingredients.map((ingredient, idx) => (
                <IngredientCard key={idx} {...ingredient} />
              ))}
            </div>
          </ScrollReveal>

          <ScrollReveal variant="fade-up" delay={300}>
            <div style={{ marginBottom: "32px" }}>
              <ExcipientCollapse ingredients={mockReport.inactive_ingredients} />
            </div>
          </ScrollReveal>

          <ScrollReveal variant="fade-up" delay={400}>
            <div style={{ marginBottom: "48px" }}>
              <SafetyModule profile={mockReport.safety_profile} />
            </div>
          </ScrollReveal>

          <ScrollReveal variant="fade-in" delay={500}>
            <div style={{ backgroundColor: "var(--surface-alt)", borderRadius: "12px", padding: "16px", fontSize: "12px", color: "var(--text-muted)", fontFamily: "monospace", textAlign: "center", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              Audit Hash: {mockReport.audit_hash}
            </div>
          </ScrollReveal>

        </div>
      </div>
    </div>
  );
}
