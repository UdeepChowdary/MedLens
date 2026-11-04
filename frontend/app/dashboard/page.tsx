"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { IcoScan, IcoArrow, IcoShield } from "@/components/Icons";
import { useAuth } from "@/context/AuthContext";
import { getAnalyses, AnalysisSummary } from "@/lib/api";

export default function DashboardOverviewPage() {
  const { user } = useAuth();
  const [recentScans, setRecentScans] = useState<AnalysisSummary[]>([]);
  const [isLoadingScans, setIsLoadingScans] = useState(true);

  useEffect(() => {
    let isMounted = true;
    getAnalyses(4).then(({ data }) => {
      if (!isMounted) return;
      if (data && data.length > 0) {
        setRecentScans(data);
      }
      setIsLoadingScans(false);
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const displayName = user?.displayName || (user?.email ? user.email.split("@")[0] : "User");

  return (
    <div style={{ padding: "32px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Welcome back, {displayName}
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Here is an overview of your medicine packaging verification hub and clinical safety tools.
      </p>

      {/* Quick Actions (3 Column Grid) */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "20px", marginBottom: "40px" }}>
        {/* Action 1: Scan New Medicine */}
        <Link href="/dashboard/scan" style={{ textDecoration: "none" }}>
          <div
            style={{
              backgroundColor: "var(--blue)",
              borderRadius: "16px",
              padding: "24px",
              color: "white",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "16px",
              boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.3)",
              transition: "transform 0.2s",
              height: "100%",
            }}
            className="hover:-translate-y-1"
          >
            <div style={{ backgroundColor: "rgba(255, 255, 255, 0.2)", padding: "12px", borderRadius: "12px" }}>
              <IcoScan size={26} color="white" />
            </div>
            <div>
              <h3 style={{ fontSize: "17px", fontWeight: 700, marginBottom: "4px" }}>Scan Medicine Packaging</h3>
              <p style={{ fontSize: "13px", opacity: 0.9, lineHeight: 1.4 }}>Identify salts and verify packaging safety instantly.</p>
            </div>
          </div>
        </Link>

        {/* Action 2: Health Profile & Allergies */}
        <Link href="/dashboard/profile" style={{ textDecoration: "none" }}>
          <div
            style={{
              backgroundColor: "white",
              border: "1px solid var(--border)",
              borderRadius: "16px",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "16px",
              boxShadow: "var(--shadow-sm)",
              transition: "transform 0.2s",
              height: "100%",
            }}
            className="hover:-translate-y-1"
          >
            <div style={{ backgroundColor: "var(--surface-alt)", padding: "12px", borderRadius: "12px" }}>
              <IcoShield size={26} color="var(--blue)" />
            </div>
            <div>
              <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                Health Profile &amp; BYOK
              </h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Configure allergies, conditions, and Gemini API key.
              </p>
            </div>
          </div>
        </Link>

        {/* Action 3: Compare by Disease */}
        <Link href="/dashboard/compare" style={{ textDecoration: "none" }}>
          <div
            style={{
              backgroundColor: "white",
              border: "1px solid var(--border)",
              borderRadius: "16px",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "16px",
              boxShadow: "var(--shadow-sm)",
              transition: "transform 0.2s",
              height: "100%",
            }}
            className="hover:-translate-y-1"
          >
            <div style={{ backgroundColor: "#eff6ff", padding: "12px", borderRadius: "12px" }}>
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
            </div>
            <div>
              <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                Compare by Disease
              </h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Find bioequivalent brands across 8 common ailments.
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Scans Section */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: "bold", color: "var(--text-primary)", margin: 0 }}>
          Recent Packaging Scans
        </h2>
        <Link href="/dashboard/history" style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--blue)", textDecoration: "none" }}>
          View all in history →
        </Link>
      </div>
      
      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        overflow: "hidden",
        boxShadow: "var(--shadow-sm)",
        marginBottom: "32px",
      }}>
        {isLoadingScans ? (
          <div style={{ padding: "36px", textAlign: "center", color: "var(--text-secondary)", fontSize: "14px" }}>
            Loading recent analyses...
          </div>
        ) : recentScans.length > 0 ? (
          recentScans.map((item, i) => (
            <Link key={item.analysis_id} href={`/dashboard/results/${item.analysis_id}`} style={{ textDecoration: "none" }}>
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between", 
                padding: "16px 24px",
                borderBottom: i !== recentScans.length - 1 ? "1px solid var(--border)" : "none",
                transition: "background-color 0.2s"
              }} className="hover:bg-slate-50">
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <div style={{ 
                    width: "44px", 
                    height: "44px", 
                    backgroundColor: "var(--surface-blue)", 
                    borderRadius: "10px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}>
                    <IcoScan size={20} color="var(--blue)" />
                  </div>
                  <div>
                    <h4 style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "15px", marginBottom: "2px" }}>
                      {item.detected_name || "Prescription Packaging"}
                    </h4>
                    <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                      {item.active_ingredients?.join(", ") || "Active salts verified"} • {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <span style={{ 
                    fontSize: "12px", 
                    fontWeight: 600, 
                    color: item.status === "verified" ? "#059669" : "var(--blue)", 
                    backgroundColor: item.status === "verified" ? "#ecfdf5" : "var(--surface-blue)", 
                    padding: "4px 10px", 
                    borderRadius: "6px" 
                  }}>
                    {item.status === "verified" ? "Verified" : "Processed"}
                  </span>
                  <IcoArrow size={16} color="var(--text-muted)" />
                </div>
              </div>
            </Link>
          ))
        ) : (
          <div style={{ padding: "40px 24px", textAlign: "center" }}>
            <div style={{ width: "48px", height: "48px", borderRadius: "50%", backgroundColor: "#eff6ff", margin: "0 auto 12px", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <IcoScan size={24} color="var(--blue)" />
            </div>
            <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
              No scans recorded yet
            </h4>
            <p style={{ fontSize: "13.5px", color: "var(--text-secondary)", maxWidth: "420px", margin: "0 auto 20px" }}>
              Snap or upload your first blister pack or medicine label to see ingredients and cross-checked contraindications.
            </p>
            <Link
              href="/dashboard/scan"
              className="btn-primary"
              style={{ display: "inline-flex", padding: "10px 20px", fontSize: "13.5px", borderRadius: "8px", textDecoration: "none" }}
            >
              Start First Scan
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
