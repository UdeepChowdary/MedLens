"use client";

import React, { useState } from "react";

// --- MOCK DATA ---
const brands = [
  { id: "dolo-650", name: "Dolo 650", manufacturer: "Micro Labs Ltd" },
  { id: "calpol-500", name: "Calpol 500", manufacturer: "GSK" },
  { id: "crocin-650", name: "Crocin 650", manufacturer: "GSK" },
  { id: "paracip-500", name: "Paracip 500", manufacturer: "Cipla" },
];

const mockComparisonData = {
  activeIngredients: [
    {
      name: "Paracetamol (Acetaminophen)",
      brandA: "650 mg",
      brandB: "500 mg",
      isDifferent: true,
      role: "Active Analgesic/Antipyretic",
    },
  ],
  inactiveIngredients: [
    {
      name: "Maize Starch",
      brandA: "Present",
      brandB: "Present",
      isDifferent: false,
    },
    {
      name: "Povidone K30",
      brandA: "Present",
      brandB: "Not Present",
      isDifferent: true,
    },
    {
      name: "Magnesium Stearate",
      brandA: "Present",
      brandB: "Present",
      isDifferent: false,
    },
    {
      name: "Sodium Methylparaben",
      brandA: "Not Present",
      brandB: "Present",
      isDifferent: true,
    },
  ],
  warnings: [
    {
      title: "Dosage Difference",
      description: "Dolo 650 contains a higher dosage of Paracetamol (650mg) compared to Calpol (500mg). Adjust intake frequency accordingly.",
      type: "amber"
    },
    {
      title: "Preservative Alert",
      description: "Calpol contains Sodium Methylparaben, which may cause allergic reactions in sensitive individuals.",
      type: "amber"
    }
  ]
};

export default function ComparePage() {
  const [brandA, setBrandA] = useState("dolo-650");
  const [brandB, setBrandB] = useState("calpol-500");
  const [isComparing, setIsComparing] = useState(false);

  const handleCompare = () => {
    setIsComparing(true);
  };

  const selectedA = brands.find(b => b.id === brandA);
  const selectedB = brands.find(b => b.id === brandB);

  return (
    <div style={{ padding: "32px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Brand Comparison
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Select two medicines to analyze their compositions side-by-side and identify therapeutic differences.
      </p>

      {/* Brand Dual Selector */}
      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        padding: "32px",
        marginBottom: "32px",
        boxShadow: "var(--shadow-sm)"
      }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "24px", justifyContent: "center" }}>
          
          {/* Selector A */}
          <div style={{ flex: "1 1 300px" }}>
            <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Medicine A
            </label>
            <select 
              value={brandA}
              onChange={(e) => { setBrandA(e.target.value); setIsComparing(false); }}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", 
                fontSize: "15px", outline: "none", backgroundColor: "var(--surface-alt)"
              }}
            >
              {brands.map(b => (
                <option key={`a-${b.id}`} value={b.id} disabled={b.id === brandB}>{b.name} ({b.manufacturer})</option>
              ))}
            </select>
          </div>

          {/* VS Badge */}
          <div style={{ 
            width: "40px", height: "40px", borderRadius: "50%", backgroundColor: "var(--blue)", 
            color: "white", display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: "bold", fontSize: "14px", alignSelf: "flex-end", marginBottom: "4px"
          }}>
            VS
          </div>

          {/* Selector B */}
          <div style={{ flex: "1 1 300px" }}>
            <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Medicine B
            </label>
            <select 
              value={brandB}
              onChange={(e) => { setBrandB(e.target.value); setIsComparing(false); }}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", 
                fontSize: "15px", outline: "none", backgroundColor: "var(--surface-alt)"
              }}
            >
              {brands.map(b => (
                <option key={`b-${b.id}`} value={b.id} disabled={b.id === brandA}>{b.name} ({b.manufacturer})</option>
              ))}
            </select>
          </div>

        </div>

        <div style={{ display: "flex", justifyContent: "center", marginTop: "32px" }}>
          <button 
            className="btn-primary" 
            onClick={handleCompare}
            disabled={isComparing}
            style={{ padding: "12px 32px", fontSize: "15px", opacity: isComparing ? 0.7 : 1 }}
          >
            {isComparing ? "Analyzing Differences..." : "Compare Formulations"}
          </button>
        </div>
      </div>

      {/* Delta Matrix Results */}
      {isComparing && (
        <div style={{ animation: "fade-up 0.5s ease-out" }}>
          
          {/* Key Differences / Warnings */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "32px" }}>
            {mockComparisonData.warnings.map((w, i) => (
              <div key={i} style={{ 
                backgroundColor: w.type === 'amber' ? "var(--warning-bg)" : "var(--surface-blue)", 
                borderLeft: `4px solid ${w.type === 'amber' ? "var(--amber)" : "var(--blue)"}`,
                padding: "16px 20px",
                borderRadius: "8px"
              }}>
                <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                  {w.title}
                </h4>
                <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  {w.description}
                </p>
              </div>
            ))}
          </div>

          {/* Table Container */}
          <div style={{ backgroundColor: "white", borderRadius: "16px", border: "1px solid var(--border)", overflow: "hidden" }}>
            
            {/* Table Header */}
            <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr", backgroundColor: "var(--surface-alt)", borderBottom: "1px solid var(--border)" }}>
              <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-secondary)", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Ingredient / Property
              </div>
              <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                {selectedA?.name}
              </div>
              <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                {selectedB?.name}
              </div>
            </div>

            {/* Active Ingredients Section */}
            <div style={{ padding: "12px 16px", backgroundColor: "var(--surface)", fontWeight: 600, fontSize: "14px", color: "var(--blue)", borderBottom: "1px solid var(--border)" }}>
              Active Ingredients (API)
            </div>
            
            {mockComparisonData.activeIngredients.map((item, i) => (
              <div key={`act-${i}`} style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr", borderBottom: "1px solid var(--border)", backgroundColor: item.isDifferent ? "var(--warning-bg)" : "transparent" }}>
                <div style={{ padding: "16px" }}>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>{item.name}</div>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{item.role}</div>
                </div>
                <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center", fontWeight: item.isDifferent ? 600 : 400 }}>
                  {item.brandA}
                </div>
                <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center", fontWeight: item.isDifferent ? 600 : 400 }}>
                  {item.brandB}
                </div>
              </div>
            ))}

            {/* Inactive Ingredients Section */}
            <div style={{ padding: "12px 16px", backgroundColor: "var(--surface)", fontWeight: 600, fontSize: "14px", color: "var(--text-secondary)", borderBottom: "1px solid var(--border)" }}>
              Inactive Ingredients (Excipients)
            </div>
            
            {mockComparisonData.inactiveIngredients.map((item, i) => (
              <div key={`inact-${i}`} style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr", borderBottom: i !== mockComparisonData.inactiveIngredients.length - 1 ? "1px solid var(--border)" : "none", backgroundColor: item.isDifferent ? "var(--warning-bg)" : "transparent" }}>
                <div style={{ padding: "16px", display: "flex", alignItems: "center" }}>
                  <span style={{ fontWeight: 500, color: "var(--text-primary)" }}>{item.name}</span>
                </div>
                <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center" }}>
                  <span style={{ 
                    padding: "4px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600,
                    backgroundColor: item.brandA === "Present" ? "var(--green-dim)" : "var(--red-dim)",
                    color: item.brandA === "Present" ? "var(--green)" : "var(--red)",
                  }}>
                    {item.brandA}
                  </span>
                </div>
                <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center" }}>
                  <span style={{ 
                    padding: "4px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600,
                    backgroundColor: item.brandB === "Present" ? "var(--green-dim)" : "var(--red-dim)",
                    color: item.brandB === "Present" ? "var(--green)" : "var(--red)",
                  }}>
                    {item.brandB}
                  </span>
                </div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  );
}
