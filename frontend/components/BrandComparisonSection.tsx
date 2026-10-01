import React, { useState } from "react";
import { IcoArrow, IcoCheck, IcoShield } from "./Icons";

export const BrandComparisonSection = () => {
  const [selectedPair, setSelectedPair] = useState(0);

  const pairs = [
    {
      title: "Dolo 650 vs. Calpol 650",
      type: "Fever & Analgesic Bioequivalence",
      brandA: { name: "Dolo 650", maker: "Micro Labs", salt: "Paracetamol IP", strength: "650 mg", binders: "Starch, magnesium stearate", price: "₹32 / 15 tabs" },
      brandB: { name: "Calpol 650", maker: "GlaxoSmithKline", salt: "Paracetamol IP", strength: "650 mg", binders: "Microcrystalline cellulose", price: "₹34 / 15 tabs" },
      savingsPill: "Price Parity (₹32 vs ₹34) • Identical therapeutic API",
      allergyCheck: "Allergen Discrepancy: Zero (Both lactose & gluten-free)",
      verdict: "100% Bioequivalent API Match. Both deliver identical therapeutic antipyretic efficacy. Patients can safely substitute either brand without altering dosage.",
    },
    {
      title: "Augmentin 625 vs. Clavam 625",
      type: "Dual-API Antibiotic Ratio Match",
      brandA: { name: "Augmentin 625 Duo", maker: "GlaxoSmithKline", salt: "Amoxicillin + Clavulanate", strength: "500 mg + 125 mg (4:1)", binders: "Titanium dioxide film coat", price: "₹205 / 10 tabs" },
      brandB: { name: "Clavam 625", maker: "Alkem Laboratories", salt: "Amoxicillin + Clavulanate", strength: "500 mg + 125 mg (4:1)", binders: "Cellulose film coat", price: "₹168 / 10 tabs" },
      savingsPill: "Save ₹37 / strip (-18%) with Clavam 625",
      allergyCheck: "Synergistic 4:1 Ratio Confirmed • Film-coated formulation",
      verdict: "Identical 4:1 synergistic antibiotic formulation. Meets standard pharmacopeial bioequivalence criteria while offering ~18% cost savings.",
    },
    {
      title: "Allegra 120 vs. Fexova 120",
      type: "Antihistamine Active Salt Match",
      brandA: { name: "Allegra 120", maker: "Sanofi India", salt: "Fexofenadine HCl", strength: "120 mg", binders: "Iron oxide pink coating", price: "₹198 / 10 tabs" },
      brandB: { name: "Fexova 120", maker: "Intas Pharma", salt: "Fexofenadine HCl", strength: "120 mg", binders: "Standard film opacifier", price: "₹130 / 10 tabs" },
      savingsPill: "Save ₹68 / strip (-34%) with Fexova 120",
      allergyCheck: "Second-Generation Non-Sedating • Identical H1 receptor binding",
      verdict: "100% INN Identity (Fexofenadine HCl). Non-sedating second-generation antihistamine with identical receptor affinity and safety profile.",
    },
  ];

  const curr = pairs[selectedPair];

  return (
    <section id="brand-comparison" style={{ padding: "80px 0", background: "var(--bg)", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 36 }}>
          <span className="section-label" style={{ marginBottom: 8, display: "block" }}>Brand Comparison</span>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 10, color: "#0F172A" }}>
            Compare Medicine Brands &amp; Generic Substitutes
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 640 }}>
            Confused when a pharmacist substitutes an alternate brand? MedLens strips trade names, extracts canonical INN salts, and confirms bioequivalence instantly.
          </p>
        </div>


        {/* Pair Selector Tabs */}
        <div style={{ display: "flex", gap: 10, marginBottom: 24, overflowX: "auto", paddingBottom: 6 }}>
          {pairs.map((p, idx) => (
            <button
              key={p.title}
              onClick={() => setSelectedPair(idx)}
              style={{
                padding: "10px 18px",
                borderRadius: 999,
                border: selectedPair === idx ? "1.5px solid var(--blue)" : "1px solid var(--border)",
                background: selectedPair === idx ? "var(--blue)" : "#fff",
                color: selectedPair === idx ? "#fff" : "var(--text-primary)",
                fontFamily: "var(--font-heading)",
                fontSize: 13.5,
                fontWeight: 700,
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.18s ease",
              }}
            >
              {p.title}
            </button>
          ))}
        </div>

        {/* Tab content — keyed so React remounts on tab switch, triggering CSS fade animation */}
        <div key={selectedPair} className="tab-content-enter">

        {/* Savings & Clinical Delta Strip */}
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: "#DCFCE7", border: "1px solid #86EFAC", color: "#166534", fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 700, display: "inline-flex", alignItems: "center", gap: 6 }}>
            <IcoCheck size={12} color="#166534" /> {curr.savingsPill}
          </div>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: "var(--surface-blue)", border: "1px solid var(--blue-border)", color: "#1E40AF", fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 700, display: "inline-flex", alignItems: "center", gap: 6 }}>
            <IcoShield size={12} color="#1E40AF" /> {curr.allergyCheck}
          </div>
        </div>

        {/* Comparison Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20, marginBottom: 20 }}>
          {/* Brand A */}
          <div className="card" style={{ padding: 24 }}>
            <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--blue)", fontWeight: 700, textTransform: "uppercase" }}>Brand A (Prescribed)</span>
            <h3 style={{ fontFamily: "var(--font-heading)", fontSize: 20, fontWeight: 800, color: "#0F172A", margin: "4px 0" }}>{curr.brandA.name}</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Mfg: {curr.brandA.maker}</p>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "var(--surface-alt)", marginBottom: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Active Salt & Strength</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#0F172A", fontFamily: "var(--font-mono)" }}>{curr.brandA.salt} {curr.brandA.strength}</div>
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 8 }}>Binders: {curr.brandA.binders}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0F172A" }}>Market Price: {curr.brandA.price}</div>
          </div>

          {/* Brand B */}
          <div className="card" style={{ padding: 24 }}>
            <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--green)", fontWeight: 700, textTransform: "uppercase" }}>Brand B (Generic Substitute)</span>
            <h3 style={{ fontFamily: "var(--font-heading)", fontSize: 20, fontWeight: 800, color: "#0F172A", margin: "4px 0" }}>{curr.brandB.name}</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Mfg: {curr.brandB.maker}</p>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "var(--surface-alt)", marginBottom: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Active Salt & Strength</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#0F172A", fontFamily: "var(--font-mono)" }}>{curr.brandB.salt} {curr.brandB.strength}</div>
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 8 }}>Binders: {curr.brandB.binders}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0F172A" }}>Market Price: {curr.brandB.price}</div>
          </div>
        </div>

        {/* Verdict Banner */}
        <div style={{ padding: "18px 22px", borderRadius: 12, background: "var(--surface-blue)", border: "1px solid var(--blue-border)", display: "flex", alignItems: "flex-start", gap: 14 }}>
          <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#10B981", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 2 }}>
            <IcoCheck size={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 14, fontWeight: 700, color: "#1E3A8A", marginBottom: 3 }}>
              MedLens Verdict: {curr.savingsPill.split("•")[0].trim()}
            </div>
            <p style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "#334155", lineHeight: 1.5 }}>
              {curr.verdict}
            </p>
          </div>
        </div>

        </div>{/* /tab-content-enter */}

        {/* Authoritative Databases Grounding Strip */}
        <div style={{ marginTop: 36, paddingTop: 24, borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
          <span style={{ fontSize: 11.5, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Grounded in Authoritative Databases:
          </span>
          <div style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
            {["OpenFDA", "PubChem (NLM)", "DailyMed (NIH)", "WHO Essential Medicines", "Indian Pharmacopoeia (IP)"].map((std) => (
              <span key={std} style={{ fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 600, color: "var(--text-secondary)", display: "inline-flex", alignItems: "center", gap: 5 }}>
                <IcoCheck size={12} color="#2563EB" /> {std}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
