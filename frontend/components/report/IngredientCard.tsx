import React from "react";
import Badge from "../ui/Badge";
import MonospaceValue from "../ui/MonospaceValue";
import { IcoFile, IcoBrain } from "../Icons";

export interface EvidenceSource {
  name: string;
  url: string;
}

export interface IngredientReportProps {
  canonical_name: string;
  raw_label_text: string;
  strength: string;
  numeric_value?: number;
  unit: string;
  role: string;
  confidence: number;
  explanation: string;
  therapeutic_purpose: string;
  evidence_sources: EvidenceSource[];
}

export default function IngredientCard(props: IngredientReportProps) {
  const status = props.confidence >= 0.9 ? "verified" : props.confidence >= 0.7 ? "medium" : "unverified";
  
  return (
    <div style={{ backgroundColor: "white", borderRadius: "12px", padding: "24px", boxShadow: "var(--shadow-sm)", border: "1px solid var(--border)", marginBottom: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "16px", marginBottom: "16px" }}>
        <div>
          <h3 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px", margin: "0 0 4px 0" }}>
            {props.canonical_name}
          </h3>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", fontFamily: "monospace", margin: 0 }}>Found as: &ldquo;{props.raw_label_text}&rdquo;</p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "8px" }}>
          <MonospaceValue value={props.numeric_value || props.strength} unit={props.unit} className="text-xl text-[var(--blue)] bg-[var(--blue)]/5 px-3 py-1 rounded-lg" />
          <Badge status={status} />
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "24px" }}>
        <div style={{ backgroundColor: "var(--surface)", borderRadius: "8px", padding: "16px", border: "1px solid var(--border)" }}>
          <h4 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 8px 0" }}>
            <IcoBrain size={16} color="var(--blue)" /> What it does
          </h4>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
            {props.explanation}
          </p>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>Therapeutic Purpose</h4>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>{props.therapeutic_purpose}</p>
        </div>

        <div style={{ paddingTop: "16px", marginTop: "16px", borderTop: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <h4 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", margin: 0 }}>
            <IcoFile size={12} color="var(--text-muted)" /> Evidence Sources
          </h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {props.evidence_sources.map((src, idx) => (
              <a 
                key={idx} 
                href={src.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-[var(--blue)] bg-[var(--blue)]/10 hover:bg-[var(--blue)]/20 px-2 py-1 rounded transition-colors"
              >
                {src.name}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
