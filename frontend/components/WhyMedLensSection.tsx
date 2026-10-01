import React from "react";
import { IcoArrow, IcoX, IcoCheck } from "./Icons";

export const WhyMedLensSection = () => {
  const tableRows = [
    { label: "Design", ai: "General-purpose conversational chatbot", ml: "Purpose-built for pharmaceutical label analysis" },
    { label: "Input", ai: "User must formulate exact medical prompts", ml: "Image-first — label composition parsed automatically" },
    { label: "Analysis", ai: "Unconstrained text generation (hallucination risk)", ml: "Deterministic entity extraction & INN normalization" },
    { label: "Evidence", ai: "Unverified internal training memory", ml: "Real-time grounding in OpenFDA, PubChem & DailyMed" },
    { label: "Output", ai: "Unstructured conversational paragraphs", ml: "Clinically structured report + confidence telemetry" },
    { label: "Equivalence", ai: "Manual querying brand by brand", ml: "Automated Active Salt & Excipient Delta Matcher" },
  ];

  return (
    <section id="why-medlens" style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
            <div>
              <span className="section-label" style={{ marginBottom: 8, display: "block" }}>Why MedLens</span>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 10, color: "#0F172A" }}>
                Built for Zero-Tolerance Medicine Verification
              </h2>
              <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 520 }}>
                General AI models are built for conversational fluency, not clinical correctness. MedLens constrains AI to a deterministic verification layer.
              </p>
            </div>
            <a href="#brand-comparison" style={{ fontFamily: "var(--font-heading)", fontSize: 14, color: "var(--blue)", textDecoration: "none", display: "flex", alignItems: "center", gap: 4, fontWeight: 700 }}>
              See brand comparison <IcoArrow />
            </a>
          </div>
        </div>

        {/* Two-Column Synchronized Comparison */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
          {/* General AI (Left, Light) */}
          <div className="card" style={{ padding: 26 }}>
            <div style={{ minHeight: 80, display: "flex", flexDirection: "column", justifyContent: "center", marginBottom: 20, borderBottom: "1px solid var(--border)", paddingBottom: 14 }}>
              <div style={{ fontFamily: "var(--font-heading)", fontSize: 18, fontWeight: 800, color: "#0F172A", marginBottom: 4 }}>
                General AI
              </div>
              <div style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-muted)" }}>
                Unconstrained Large Language Models (ChatGPT · Gemini · Claude)
              </div>
            </div>
            {tableRows.map((row) => (
              <div key={row.label} style={{ paddingBottom: 12, marginBottom: 12, borderBottom: "1px solid var(--border)", display: "grid", gridTemplateColumns: "100px 1fr", gap: 12 }}>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>{row.label}</div>
                <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span style={{ marginTop: 2, flexShrink: 0 }}><IcoX size={14} /></span>
                  <span style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.45 }}>{row.ai}</span>
                </div>
              </div>
            ))}
          </div>

          {/* MedLens (Right, Dark Sleek) */}
          <div className="ml-dark-card" style={{ padding: 26 }}>
            <div style={{ minHeight: 80, display: "flex", flexDirection: "column", justifyContent: "center", marginBottom: 20, borderBottom: "1px solid rgba(255, 255, 255, 0.10)", paddingBottom: 14 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 4 }}>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 18, fontWeight: 800, color: "#fff" }}>
                  MedLens
                </div>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "#60A5FA", padding: "3px 10px", background: "rgba(37,99,235,0.25)", borderRadius: 999, border: "1px solid rgba(37,99,235,0.35)" }}>
                  Clinical Protocol
                </span>
              </div>
              <div style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "#94A3B8" }}>
                Deterministic Medicine Verification & Normalization Engine
              </div>
            </div>
            {tableRows.map((row) => (
              <div key={row.label} className="ml-check-row">
                <div style={{ width: 20, height: 20, borderRadius: "50%", background: "#2563EB", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <IcoCheck size={11} color="#fff" />
                </div>
                <span>{row.ml}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
