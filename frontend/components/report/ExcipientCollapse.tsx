"use client";

import React, { useState } from "react";
import { IcoArrow } from "../Icons";

interface ExcipientCollapseProps {
  ingredients: { name: string; purpose: string }[];
}

export default function ExcipientCollapse({ ingredients }: ExcipientCollapseProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!ingredients || ingredients.length === 0) return null;

  return (
    <div style={{ backgroundColor: "white", borderRadius: "12px", border: "1px solid var(--border)", overflow: "hidden", marginBottom: "16px" }}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px", backgroundColor: "var(--surface)", border: "none", cursor: "pointer" }}
        aria-expanded={isOpen}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>Inactive Ingredients (Excipients)</span>
          <span style={{ backgroundColor: "var(--border)", color: "var(--text-secondary)", padding: "2px 6px", borderRadius: "4px", fontSize: "12px", fontWeight: 700 }}>{ingredients.length}</span>
        </div>
        <div style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.3s" }}>
          <IcoArrow />
        </div>
      </button>
      
      <div 
        style={{ maxHeight: isOpen ? "1000px" : "0", opacity: isOpen ? 1 : 0, overflow: "hidden", transition: "all 0.3s ease-in-out" }}
      >
        <div style={{ padding: "16px", borderTop: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "12px" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "0 0 16px 0" }}>
            Inactive ingredients (excipients) are necessary for the formulation of the medicine (e.g., tablet coating, dissolution speed, coloring) but do not have therapeutic effects themselves.
          </p>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "8px" }}>
            {ingredients.map((ing, idx) => (
              <li key={idx} style={{ display: "flex", gap: "12px", fontSize: "14px", paddingBottom: "8px", borderBottom: idx === ingredients.length - 1 ? "none" : "1px solid var(--surface)" }}>
                <span style={{ fontWeight: 500, color: "var(--text-primary)", minWidth: "150px" }}>{ing.name}</span>
                <span style={{ color: "var(--text-secondary)" }}>{ing.purpose}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
