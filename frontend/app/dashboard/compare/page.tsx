"use client";

import React, { useState } from "react";
import { compareProducts, ComparisonResponse, ComparisonOutcome } from "@/lib/api";

const PRODUCT_CATALOG = [
  { id: "dolo-650", name: "Dolo 650", manufacturer: "Micro Labs Ltd" },
  { id: "calpol-500", name: "Calpol 500", manufacturer: "GSK" },
  { id: "crocin-650", name: "Crocin 650", manufacturer: "GSK" },
  { id: "paracip-500", name: "Paracip 500", manufacturer: "Cipla" },
  { id: "augmentin-625", name: "Augmentin 625 Duo", manufacturer: "GSK" },
  { id: "cetirizine-10", name: "Cetirizine 10mg", manufacturer: "Cipla" },
  { id: "brufen-400", name: "Brufen 400", manufacturer: "Abbott" },
  { id: "combiflam", name: "Combiflam", manufacturer: "Sanofi" },
  { id: "glucophage-500", name: "Glucophage 500mg", manufacturer: "Sun Pharma" },
  { id: "lipitor-10", name: "Lipitor 10mg", manufacturer: "Pfizer" },
  { id: "omez-20", name: "Omez 20mg", manufacturer: "Dr. Reddy's" },
  { id: "zithromax-500", name: "Zithromax 500mg", manufacturer: "Pfizer" },
  { id: "pantodac-40", name: "Pantodac 40", manufacturer: "Zydus" },
  { id: "ecosprin-75", name: "Ecosprin 75", manufacturer: "USV Ltd" },
  { id: "montek-10", name: "Montek LC 10", manufacturer: "Sun Pharma" },
  { id: "losartan-50", name: "Losartan 50", manufacturer: "Cipla" },
  { id: "amlodac-5", name: "Amlodac 5", manufacturer: "Zydus" },
  { id: "vomistop-10", name: "Vomistop 10", manufacturer: "Meyer" },
];

function resultBadgeStyle(result: ComparisonOutcome): React.CSSProperties {
  switch (result) {
    case "match":
      return { backgroundColor: "var(--green-dim, #dcfce7)", color: "var(--green, #16a34a)", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    case "difference":
      return { backgroundColor: "var(--warning-bg, #fffbeb)", color: "var(--amber, #d97706)", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    case "conflict":
      return { backgroundColor: "var(--red-dim, #fee2e2)", color: "var(--red, #dc2626)", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
    default:
      return { backgroundColor: "var(--surface-alt, #f1f5f9)", color: "var(--text-muted, #94a3b8)", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 600 };
  }
}

export default function ComparePage() {
  const [brandA, setBrandA] = useState("dolo-650");
  const [brandB, setBrandB] = useState("calpol-500");
  const [isComparing, setIsComparing] = useState(false);
  const [compareResult, setCompareResult] = useState<ComparisonResponse | null>(null);
  const [compareError, setCompareError] = useState<string | null>(null);

  const selectedA = PRODUCT_CATALOG.find((b) => b.id === brandA);
  const selectedB = PRODUCT_CATALOG.find((b) => b.id === brandB);

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

  const handleReset = () => {
    setCompareResult(null);
    setCompareError(null);
  };

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
              onChange={(e) => { setBrandA(e.target.value); handleReset(); }}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)",
                fontSize: "15px", outline: "none", backgroundColor: "var(--surface-alt)"
              }}
            >
              {PRODUCT_CATALOG.map((b) => (
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
              onChange={(e) => { setBrandB(e.target.value); handleReset(); }}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)",
                fontSize: "15px", outline: "none", backgroundColor: "var(--surface-alt)"
              }}
            >
              {PRODUCT_CATALOG.map((b) => (
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

      {/* Loading Spinner */}
      {isComparing && (
        <div style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ width: "48px", height: "48px", borderRadius: "50%", border: "3px solid var(--blue)", borderTopColor: "transparent", margin: "0 auto 16px", animation: "spin 0.8s linear infinite" }} />
          <p style={{ color: "var(--text-secondary)" }}>Comparing formulations...</p>
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

          {/* Warnings Section */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "32px" }}>
            {compareResult.strength_delta?.warning && (
              <div style={{
                backgroundColor: "var(--warning-bg, #fffbeb)",
                borderLeft: "4px solid var(--amber, #d97706)",
                padding: "16px 20px",
                borderRadius: "8px"
              }}>
                <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Strength Difference
                </h4>
                <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  {compareResult.strength_delta.warning}
                  {compareResult.strength_delta.numeric_delta !== undefined && (
                    <span style={{ fontWeight: 600 }}> (Delta: {compareResult.strength_delta.numeric_delta}{compareResult.strength_delta.unit ?? ""})</span>
                  )}
                </p>
              </div>
            )}
            {compareResult.therapeutic_equivalence?.note && (
              <div style={{
                backgroundColor: "var(--surface-blue, #eff6ff)",
                borderLeft: "4px solid var(--blue, #2563eb)",
                padding: "16px 20px",
                borderRadius: "8px"
              }}>
                <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Therapeutic Equivalence
                </h4>
                <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  <strong>{compareResult.therapeutic_equivalence.status}:</strong> {compareResult.therapeutic_equivalence.note}
                </p>
              </div>
            )}
          </div>

          {/* Attribute Comparison Table */}
          {compareResult.attributes.length > 0 && (
            <div style={{ backgroundColor: "white", borderRadius: "16px", border: "1px solid var(--border)", overflow: "hidden", marginBottom: "24px" }}>
              {/* Table Header */}
              <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr", backgroundColor: "var(--surface-alt)", borderBottom: "1px solid var(--border)" }}>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-secondary)", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Attribute
                </div>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                  {selectedA?.name ?? compareResult.medicine_a.name}
                </div>
                <div style={{ padding: "16px", fontWeight: 700, color: "var(--text-primary)", fontSize: "15px", borderLeft: "1px solid var(--border)" }}>
                  {selectedB?.name ?? compareResult.medicine_b.name}
                </div>
              </div>

              {/* Active Ingredients Section */}
              <div style={{ padding: "12px 16px", backgroundColor: "var(--surface)", fontWeight: 600, fontSize: "14px", color: "var(--blue)", borderBottom: "1px solid var(--border)" }}>
                Active Ingredients (API)
              </div>

              {compareResult.attributes.map((attr, i) => (
                <div key={i} style={{
                  display: "grid",
                  gridTemplateColumns: "1.5fr 1fr 1fr",
                  borderBottom: i !== compareResult.attributes.length - 1 ? "1px solid var(--border)" : "none",
                  backgroundColor: attr.result === "difference" || attr.result === "conflict" ? "var(--warning-bg, #fffbeb)" : "transparent"
                }}>
                  <div style={{ padding: "16px" }}>
                    <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>{attr.field}</div>
                    {attr.reason && <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{attr.reason}</div>}
                  </div>
                  <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={resultBadgeStyle(attr.result)}>{attr.result}</span>
                  </div>
                  <div style={{ padding: "16px", borderLeft: "1px solid var(--border)", display: "flex", alignItems: "center", fontSize: "13px", color: "var(--text-secondary)" }}>
                    {attr.evidence.join("; ")}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Excipient Differences */}
          {compareResult.excipient_differences.length > 0 && (
            <div style={{ backgroundColor: "white", borderRadius: "12px", border: "1px solid var(--border)", padding: "20px", marginBottom: "24px" }}>
              <h4 style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "12px", fontSize: "16px" }}>Excipient Differences</h4>
              <ul style={{ paddingLeft: "20px", margin: 0, color: "var(--text-secondary)", fontSize: "14px", display: "flex", flexDirection: "column", gap: "6px" }}>
                {compareResult.excipient_differences.map((diff, i) => <li key={i}>{diff}</li>)}
              </ul>
            </div>
          )}

          {/* Limitations */}
          {compareResult.limitations.length > 0 && (
            <div style={{ backgroundColor: "var(--surface-alt)", borderRadius: "12px", padding: "16px 20px" }}>
              <h4 style={{ fontWeight: 600, color: "var(--text-muted)", marginBottom: "8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Limitations</h4>
              <ul style={{ paddingLeft: "20px", margin: 0, color: "var(--text-secondary)", fontSize: "13px", display: "flex", flexDirection: "column", gap: "4px" }}>
                {compareResult.limitations.map((l, i) => <li key={i}>{l}</li>)}
              </ul>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
