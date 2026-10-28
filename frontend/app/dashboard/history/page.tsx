"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { IcoScan, IcoArrow, IcoShield } from "@/components/Icons";
import { getAnalyses, AnalysisSummary } from "@/lib/api";

export default function HistoryPage() {
  const [scans, setScans] = useState<AnalysisSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchHistory = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    const { data, error } = await getAnalyses(50);
    if (error) {
      setErrorMessage(error.message);
    } else if (data) {
      setScans(data);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredScans = scans.filter((scan) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    const nameMatch = scan.detected_name.toLowerCase().includes(q);
    const ingMatch = scan.active_ingredients.some((ing) => ing.toLowerCase().includes(q));
    return nameMatch || ingMatch;
  });

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "verified":
        return { label: "Verified", bg: "var(--surface-green)", text: "var(--green)" };
      case "partially_verified":
        return { label: "Partially Verified", bg: "var(--surface-blue)", text: "var(--blue)" };
      case "needs_confirmation":
        return { label: "Needs Confirmation", bg: "var(--surface-amber)", text: "var(--amber)" };
      case "unable_to_verify":
      default:
        return { label: "Unverified", bg: "var(--surface-alt)", text: "var(--text-muted)" };
    }
  };

  return (
    <div style={{ padding: "32px", maxWidth: "1000px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
            Scan History
          </h1>
          <p style={{ color: "var(--text-secondary)" }}>
            Review your previously scanned medicines, verification states, and clinical monographs.
          </p>
        </div>

        <Link
          href="/dashboard/scan"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            backgroundColor: "var(--blue)",
            color: "white",
            padding: "10px 18px",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "14px",
            textDecoration: "none",
            boxShadow: "0 2px 4px rgba(37,99,235,0.2)",
          }}
        >
          <IcoScan size={18} color="white" />
          <span>New Scan</span>
        </Link>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: "24px" }}>
        <input
          type="text"
          placeholder="Search by brand name or active ingredient (e.g. Dolo, Paracetamol, Metformin)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: "100%",
            padding: "12px 16px",
            borderRadius: "10px",
            border: "1px solid var(--border)",
            backgroundColor: "white",
            fontSize: "15px",
            color: "var(--text-primary)",
            outline: "none",
          }}
        />
      </div>

      {errorMessage && (
        <div style={{ marginBottom: "24px", padding: "16px", backgroundColor: "var(--red-dim, #fee2e2)", borderLeft: "4px solid var(--red, #ef4444)", borderRadius: "8px", color: "var(--red, #dc2626)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span><strong>Error:</strong> {errorMessage}</span>
          <button onClick={fetchHistory} style={{ background: "none", border: "underline", color: "inherit", fontWeight: 600, cursor: "pointer" }}>
            Retry
          </button>
        </div>
      )}

      {/* List Container */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        overflow: "hidden",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        {isLoading ? (
          <div style={{ padding: "48px", textAlign: "center", color: "var(--text-secondary)" }}>
            <div className="animate-spin" style={{ width: "32px", height: "32px", border: "3px solid var(--border)", borderTopColor: "var(--blue)", borderRadius: "50%", margin: "0 auto 16px" }} />
            <p>Loading your scan history...</p>
          </div>
        ) : filteredScans.length === 0 ? (
          <div style={{ padding: "64px 24px", textAlign: "center" }}>
            <div style={{ width: "64px", height: "64px", backgroundColor: "var(--surface-blue)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
              <IcoScan size={28} color="var(--blue)" />
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              {searchQuery ? "No matching scans found" : "No medicine scans yet"}
            </h3>
            <p style={{ color: "var(--text-secondary)", maxWidth: "420px", margin: "0 auto 24px", fontSize: "14px", lineHeight: "1.5" }}>
              {searchQuery
                ? `No scanned medicines match "${searchQuery}". Try searching for another brand name or chemical salt.`
                : "Capture or upload packaging photos of any medicine strip or bottle to verify composition, contraindications, and active salts."}
            </p>
            {!searchQuery && (
              <Link
                href="/dashboard/scan"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  backgroundColor: "var(--blue)",
                  color: "white",
                  padding: "10px 20px",
                  borderRadius: "8px",
                  fontWeight: 600,
                  fontSize: "14px",
                  textDecoration: "none",
                }}
              >
                Scan Your First Medicine
              </Link>
            )}
          </div>
        ) : (
          filteredScans.map((item, i) => {
            const badge = getStatusBadge(item.status);
            const dateStr = new Date(item.created_at).toLocaleDateString("en-IN", {
              month: "short",
              day: "numeric",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            });

            return (
              <Link key={item.analysis_id} href={`/dashboard/results/${item.analysis_id}`} style={{ textDecoration: "none" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "18px 24px",
                    borderBottom: i !== filteredScans.length - 1 ? "1px solid var(--border)" : "none",
                    transition: "background-color 0.15s ease",
                  }}
                  className="hover:bg-slate-50"
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <div style={{
                      width: "48px",
                      height: "48px",
                      backgroundColor: "var(--surface-blue)",
                      borderRadius: "10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}>
                      <IcoScan size={22} color="var(--blue)" />
                    </div>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                        <h4 style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "16px", margin: 0 }}>
                          {item.detected_name}
                        </h4>
                        <span style={{ fontSize: "12px", color: "var(--text-muted)", backgroundColor: "var(--surface-alt)", padding: "2px 6px", borderRadius: "4px" }}>
                          {item.dosage_form}
                        </span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
                        <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
                          {dateStr}
                        </p>
                        {item.active_ingredients.length > 0 && (
                          <span style={{ fontSize: "12px", color: "var(--blue)", fontWeight: 500 }}>
                            {item.active_ingredients.join(" + ")}
                          </span>
                        )}
                        {item.processing_time_ms > 0 && (
                          <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                            • {(item.processing_time_ms / 1000).toFixed(1)}s
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <span style={{
                      fontSize: "12px",
                      fontWeight: 600,
                      color: badge.text,
                      backgroundColor: badge.bg,
                      padding: "4px 10px",
                      borderRadius: "6px",
                      whiteSpace: "nowrap",
                    }}>
                      {badge.label}
                    </span>
                    <IcoArrow size={16} color="var(--text-muted)" />
                  </div>
                </div>
              </Link>
            );
          })
        )}
      </div>
    </div>
  );
}
