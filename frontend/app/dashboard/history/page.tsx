"use client";

import React from "react";
import Link from "next/link";
import { IcoScan, IcoArrow } from "@/components/Icons";

export default function HistoryPage() {
  return (
    <div style={{ padding: "32px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Scan History
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Review your previously scanned medicines and their safety reports.
      </p>

      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        overflow: "hidden" 
      }}>
        {[
          { id: "test-123", name: "Dolo 650", date: "Today, 9:42 AM", status: "Verified", color: "var(--green)" },
          { id: "test-124", name: "Allegra 120mg", date: "Yesterday, 2:15 PM", status: "Warning", color: "var(--amber)" },
          { id: "test-125", name: "Unknown Supplement", date: "Oct 2, 2026", status: "Unknown", color: "var(--text-muted)" },
          { id: "test-126", name: "Calpol 500", date: "Sep 28, 2026", status: "Verified", color: "var(--green)" },
          { id: "test-127", name: "Cetirizine 10mg", date: "Sep 25, 2026", status: "Verified", color: "var(--green)" }
        ].map((item, i) => (
          <Link key={i} href={`/dashboard/results/${item.id}`} style={{ textDecoration: "none" }}>
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "space-between", 
              padding: "16px 24px",
              borderBottom: i !== 4 ? "1px solid var(--border)" : "none",
              transition: "background-color 0.2s"
            }} className="hover:bg-slate-50">
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <div style={{ 
                  width: "48px", 
                  height: "48px", 
                  backgroundColor: "var(--surface-blue)", 
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <IcoScan size={20} color="var(--blue)" />
                </div>
                <div>
                  <h4 style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "15px" }}>{item.name}</h4>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{item.date}</p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <span style={{ 
                  fontSize: "12px", 
                  fontWeight: 600, 
                  color: item.color, 
                  backgroundColor: `${item.color}15`, 
                  padding: "4px 10px", 
                  borderRadius: "4px" 
                }}>
                  {item.status}
                </span>
                <IcoArrow size={18} color="var(--text-muted)" />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
