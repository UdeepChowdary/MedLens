import React from "react";
import { IcoX } from "../Icons"; // Will use IcoX for warnings

export interface SafetyProfile {
  purpose_summary: string;
  precautions: string[];
  contraindications: string[];
  adverse_effects: string[];
}

interface SafetyModuleProps {
  profile: SafetyProfile;
}

export default function SafetyModule({ profile }: SafetyModuleProps) {
  return (
    <div style={{ backgroundColor: "#fff1f2", borderRadius: "12px", padding: "24px", border: "1px solid #ffe4e6", marginBottom: "16px" }}>
      <h3 style={{ fontSize: "20px", fontWeight: 700, color: "#881337", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px", margin: "0 0 16px 0" }}>
        <span style={{ backgroundColor: "#fecdd3", color: "#be123c", padding: "4px", borderRadius: "4px", display: "flex" }}><IcoX size={16} /></span>
        Safety & Precautions
      </h3>
      
      <p style={{ color: "#9f1239", fontSize: "14px", fontWeight: 500, margin: "0 0 24px 0" }}>
        {profile.purpose_summary}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "24px" }}>
        {profile.contraindications.length > 0 && (
          <div style={{ flex: "1 1 300px" }}>
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#881337", textTransform: "uppercase", letterSpacing: "0.5px", margin: "0 0 8px 0" }}>Contraindications (Do Not Use If)</h4>
            <ul style={{ paddingLeft: "20px", margin: 0, color: "#9f1239", fontSize: "14px", display: "flex", flexDirection: "column", gap: "4px" }}>
              {profile.contraindications.map((item, idx) => <li key={idx} style={{ marginBottom: "4px" }}>{item}</li>)}
            </ul>
          </div>
        )}

        {profile.precautions.length > 0 && (
          <div style={{ flex: "1 1 300px" }}>
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#881337", textTransform: "uppercase", letterSpacing: "0.5px", margin: "0 0 8px 0" }}>General Precautions</h4>
            <ul style={{ paddingLeft: "20px", margin: 0, color: "#9f1239", fontSize: "14px", display: "flex", flexDirection: "column", gap: "4px" }}>
              {profile.precautions.map((item, idx) => <li key={idx} style={{ marginBottom: "4px" }}>{item}</li>)}
            </ul>
          </div>
        )}

        {profile.adverse_effects.length > 0 && (
          <div style={{ flex: "1 1 100%", marginTop: "8px" }}>
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#881337", textTransform: "uppercase", letterSpacing: "0.5px", margin: "0 0 8px 0" }}>Possible Adverse Effects</h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {profile.adverse_effects.map((item, idx) => (
                <span key={idx} style={{ backgroundColor: "rgba(255, 255, 255, 0.6)", color: "#9f1239", padding: "4px 10px", borderRadius: "4px", fontSize: "12px", fontWeight: 500, border: "1px solid #fecdd3" }}>
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div style={{ marginTop: "24px", paddingTop: "16px", borderTop: "1px solid rgba(254, 205, 211, 0.5)" }}>
        <p style={{ fontSize: "12px", color: "rgba(190, 18, 60, 0.7)", fontStyle: "italic", margin: 0 }}>
          Disclaimer: MedLens provides informational packaging breakdowns only. Consult a healthcare professional for diagnosis or treatment decisions.
        </p>
      </div>
    </div>
  );
}
