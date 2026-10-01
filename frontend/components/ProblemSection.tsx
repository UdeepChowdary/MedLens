import React from "react";
import { IcoHelpCircle } from "./Icons";

export const ProblemSection = () => (
  <section style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
    <div className="container">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 48, alignItems: "center" }}>
        
        {/* Left Column: Context & Pain Points */}
        <div>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(26px, 3.5vw, 40px)",
              fontWeight: 800,
              letterSpacing: "-0.02em",
              marginBottom: 16,
              color: "#0F172A",
            }}
          >
            Medicine packaging is built for chemists, not patients.
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 15.5, color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: 22 }}>
            Medicine boxes are packed with chemical abbreviations, strength ratios, excipients, and regulatory warnings that make it nearly impossible to quickly know what is actually inside your pill.
          </p>

          {/* Pain Point Questions */}
          <div style={{ padding: "18px 20px", borderRadius: 12, background: "var(--surface-alt)", border: "1px solid var(--border)", marginBottom: 22 }}>
            <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--blue-dim)", border: "1.5px solid var(--blue-border)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
              <IcoHelpCircle size={16} color="var(--blue)" />
            </div>
            {[
              "\"What is the active therapeutic chemical vs. inactive binder?\"",
              "\"Is this substitute brand the exact same salt as my prescription?\"",
              "\"Why does the packaging say 'Excipients q.s.'?\"",
            ].map((q) => (
              <div key={q} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                <span style={{ color: "var(--blue)", fontSize: 14, flexShrink: 0 }}>•</span>
                <span style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "var(--text-secondary)", lineHeight: 1.5 }}>{q}</span>
              </div>
            ))}
          </div>

          {/* Tag Pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {["Chemical INN Salts", "Dosage Strengths", "Excipients q.s.", "Schedule H Warnings", "Bioequivalence Parity"].map((tag) => (
              <span
                key={tag}
                style={{
                  padding: "5px 12px",
                  borderRadius: 999,
                  border: "1px solid var(--border)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 11.5,
                  color: "var(--text-secondary)",
                  background: "#fff",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Right Column: Real Medicine Packaging Image */}
        <div style={{ position: "relative", display: "flex", justifyContent: "center", alignItems: "center" }}>
          <div
            style={{
              borderRadius: 18,
              overflow: "hidden",
              border: "1px solid var(--border)",
              boxShadow: "0 16px 40px rgba(15, 23, 42, 0.08)",
              background: "#FFFFFF",
              maxWidth: 400,
              width: "100%",
            }}
          >
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", background: "#FFFFFF", padding: "12px 12px 4px" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/c7f09fc4-8342-46ba-9471-3e4158342213.png"
                alt="Pure Nutrition Multivitamin formulation label showing complex ingredients, active salts, and excipients"
                style={{
                  maxHeight: 390,
                  maxWidth: "100%",
                  height: "auto",
                  width: "auto",
                  display: "block",
                  objectFit: "contain",
                }}
              />
            </div>
            <div style={{ padding: "14px 18px", background: "var(--surface-alt)", borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
              <div>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 13.5, fontWeight: 700, color: "#0F172A" }}>
                  Pure Nutrition Multivitamin
                </div>
                <div style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-secondary)" }}>
                  Dense formulation panel • Active salts, RDA% & Excipients
                </div>
              </div>
              <span style={{ padding: "4px 10px", borderRadius: 999, background: "#FEF2F2", border: "1px solid #FECACA", color: "#DC2626", fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                Hard-to-Read Label
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);
