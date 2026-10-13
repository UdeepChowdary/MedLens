import React from "react";
import Badge from "../ui/Badge";
import { IcoShield } from "../Icons";

interface ProductOverviewProps {
  name: string;
  manufacturer: string;
  dosageForm: string;
  confidence: number;
}

export default function ProductOverview({ name, manufacturer, dosageForm, confidence }: ProductOverviewProps) {
  const isVerified = confidence >= 0.9;
  
  return (
    <div style={{ backgroundColor: "white", borderRadius: "16px", padding: "32px", boxShadow: "var(--shadow-sm)", border: "1px solid var(--border)", marginBottom: "32px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "flex-start", gap: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
            <h1 style={{ fontSize: "30px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>{name}</h1>
            <Badge status={isVerified ? "verified" : "medium"} label={isVerified ? "Verified Product" : "Medium Confidence"} />
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "18px", margin: 0 }}>
            {manufacturer} • {dosageForm}
          </p>
        </div>
        
        <div style={{ display: "flex", alignItems: "center", gap: "12px", backgroundColor: "var(--surface)", padding: "16px", borderRadius: "12px", border: "1px solid var(--border)" }}>
          <div style={{ width: "48px", height: "48px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "rgba(37, 99, 235, 0.1)", color: "var(--blue)" }}>
            <IcoShield size={24} />
          </div>
          <div>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)", fontWeight: 500, margin: 0 }}>Overall Confidence</p>
            <p style={{ fontSize: "24px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>{(confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
