import React from "react";
import { ScrollReveal } from "./ScrollReveal";
import { IcoCheck, IcoFile, IcoShield, IcoBrain, IcoScan } from "./Icons";

export const HowItWorksSection = () => {
  const steps = [
    { n: 1, label: "Scan / Upload", icon: <IcoScan size={20} color="#fff" />, items: ["Tablet strip", "Medicine box", "Syrup bottle", "Composition panel"] },
    { n: 2, label: "Extract", icon: <IcoFile size={20} color="#fff" />, items: ["Medicine trade name", "Strengths & dosages", "Prescription marks", "Manufacturer ID"] },
    { n: 3, label: "Identify & Verify", icon: <IcoShield size={20} color="#fff" />, items: ["Canonical INN mapping", "OpenFDA & PubChem", "Bioequivalence check", "Flag unverified claims"] },
    { n: 4, label: "AI Synthesis", icon: <IcoBrain size={20} color="#fff" />, items: ["Active vs inactive roles", "Therapeutic purpose", "Plain-English summary", "Contraindications"] },
    { n: 5, label: "Clinical Report", icon: <IcoFile size={20} color="#fff" />, items: ["Structured clarity", "Confidence telemetry", "Official citations", "Brand delta match"] },
  ];

  return (
    <section id="how-it-works" style={{ padding: "80px 0", background: "var(--bg)", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
            <div>
              <span className="section-label" style={{ marginBottom: 8, display: "block" }}>How It Works</span>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 8, color: "#0F172A" }}>
                From photo to verified report in 5 steps
              </h2>
              <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 520 }}>
                Every image passes through 5 disciplined verification gates — no AI hallucinations, no guesswork.
              </p>
            </div>
            <div style={{ padding: "6px 14px", borderRadius: 999, background: "var(--blue-dim)", border: "1px solid var(--blue-border)", color: "var(--blue)", fontSize: 12.5, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
              5-STAGE PIPELINE
            </div>
          </div>
        </div>

        {/* 5-Step Pipeline Flow with Connected Directional Arrows */}
        <div className="pipeline-flow-container">
          {steps.map((step, idx) => (
            <React.Fragment key={step.n}>
              <ScrollReveal variant="fade-up" delay={idx * 90} duration={580}>
                <div
                  className="card-hover pipeline-card"
                  style={{
                    padding: "20px 16px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    border: "1px solid var(--border)",
                    background: "#FFFFFF",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div className="step-circle">{step.n}</div>
                        <div style={{ width: 32, height: 32, borderRadius: 8, background: "#334155", display: "flex", alignItems: "center", justifyContent: "center" }}>
                          {step.icon}
                        </div>
                      </div>
                    </div>
                    <div style={{ fontFamily: "var(--font-heading)", fontSize: 14.5, fontWeight: 700, marginBottom: 10, color: "#0F172A" }}>
                      {step.label}
                    </div>
                    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                      {step.items.map((item) => (
                        <li key={item} style={{ display: "flex", gap: 6, marginBottom: 6 }}>
                          <span style={{ color: "var(--blue)", marginTop: 2, flexShrink: 0 }}>
                            <IcoCheck size={11} color="var(--blue)" />
                          </span>
                          <span style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                            {item}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </ScrollReveal>

              {/* Explicit Arrow pointing cleanly to next step */}
              {idx < steps.length - 1 && (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, padding: "4px 0" }}>
                  <div
                    className="pipeline-arrow-btn"
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: "var(--blue-dim)",
                      border: "1.5px solid var(--blue-border)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "0 2px 6px rgba(37, 99, 235, 0.12)",
                    }}
                  >
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" className="pipeline-arrow-svg">
                      <line x1="5" y1="12" x2="19" y2="12" /><polyline points="13 6 19 12 13 18" />
                    </svg>
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
};
