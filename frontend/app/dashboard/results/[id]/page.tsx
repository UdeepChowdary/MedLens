"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ProductOverview from "@/components/report/ProductOverview";
import IngredientCard from "@/components/report/IngredientCard";
import ExcipientCollapse from "@/components/report/ExcipientCollapse";
import SafetyModule from "@/components/report/SafetyModule";
import { ScrollReveal } from "@/components/ScrollReveal";
import { IcoArrow } from "@/components/Icons";
import { getAnalysis, AnalysisResponse } from "@/lib/api";

export default function ResultsPage() {
  const params = useParams();
  const id = typeof params?.id === "string" ? params.id : Array.isArray(params?.id) ? params.id[0] : "demo-scan";

  const [sourceImage] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem("scanned_image");
    }
    return null;
  });
  const [report, setReport] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [matchedAllergies, setMatchedAllergies] = useState<{ ingredient: string; allergy: string }[]>([]);

  useEffect(() => {
    let isMounted = true;
    getAnalysis(id).then(({ data, error }) => {
      if (!isMounted) return;
      if (error) {
        setFetchError(error.message);
      } else if (data) {
        setReport(data);

        // Cross-reference user allergies from Profile
        try {
          const stored = localStorage.getItem("medlens_user_allergies");
          const userAllergies: string[] = stored ? JSON.parse(stored) : ["Penicillin", "Ibuprofen"];
          const matches: { ingredient: string; allergy: string }[] = [];
          const allIngredients = [
            ...data.active_ingredients.map((a) => a.canonical_name),
            ...data.active_ingredients.map((a) => a.raw_label_text),
            ...data.inactive_ingredients.map((e) => e.canonical_name),
          ];

          for (const allergy of userAllergies) {
            const al = allergy.toLowerCase().trim();
            if (!al) continue;
            for (const ing of allIngredients) {
              const ingLower = ing.toLowerCase();
              if (ingLower.includes(al) || al.includes(ingLower)) {
                matches.push({ ingredient: ing, allergy });
                break;
              }
            }
          }
          setMatchedAllergies(matches);
        } catch {
          // Ignore parse errors
        }
      }
      setIsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleRetry = () => {
    setIsLoading(true);
    setFetchError(null);
    getAnalysis(id).then(({ data, error }) => {
      if (error) {
        setFetchError(error.message);
      } else if (data) {
        setReport(data);
      }
      setIsLoading(false);
    });
  };

  // Map API inactive_ingredients to ExcipientCollapse format
  const excipients =
    report?.inactive_ingredients.map((ing) => ({
      name: ing.canonical_name,
      purpose: ing.explanation,
    })) ?? [];

  return (
    <div style={{ minHeight: "100%", backgroundColor: "var(--surface)", display: "flex", flexDirection: "column" }} className="font-sans">
      <div style={{ flex: 1, paddingTop: "32px", paddingBottom: "96px", paddingLeft: "24px", paddingRight: "24px", position: "relative" }}>
        <div style={{ maxWidth: "896px", margin: "0 auto" }}>

          <ScrollReveal variant="fade-up">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }} className="print-hide">
              <Link href="/dashboard/scan" style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--blue)", fontWeight: 500, textDecoration: "none" }}>
                <span style={{ transform: "rotate(180deg)", display: "flex" }}><IcoArrow /></span>
                Back to Scanner
              </Link>

              <button
                onClick={() => window.print()}
                style={{
                  display: "inline-flex", alignItems: "center", gap: "8px",
                  backgroundColor: "white", color: "var(--text-primary)",
                  padding: "8px 16px", borderRadius: "8px",
                  border: "1px solid var(--border)", fontWeight: 600,
                  fontSize: "14px", cursor: "pointer",
                  boxShadow: "var(--shadow-sm)"
                }}
                className="hover:bg-slate-50 transition-colors"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Export PDF
              </button>
            </div>
          </ScrollReveal>

          {/* Uploaded Image Preview */}
          <ScrollReveal variant="fade-up" delay={50}>
            <div style={{ marginBottom: "24px", width: "100%", height: "220px", borderRadius: "16px", overflow: "hidden", position: "relative", backgroundColor: "#f1f5f9", border: "1px solid var(--border)" }}>
              <img
                src={sourceImage || "/placeholder-med.svg"}
                alt="Scanned Medicine Preview"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
              <div style={{ position: "absolute", bottom: "16px", right: "16px", backgroundColor: "rgba(0,0,0,0.6)", color: "white", padding: "4px 10px", borderRadius: "8px", fontSize: "12px", fontWeight: 600, backdropFilter: "blur(4px)", display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4ade80" }}></span>
                Source Image
              </div>
            </div>
          </ScrollReveal>

          {/* Loading State */}
          {isLoading && (
            <ScrollReveal variant="fade-up" delay={100}>
              <div style={{ backgroundColor: "white", borderRadius: "16px", padding: "48px", textAlign: "center", border: "1px solid var(--border)", marginBottom: "32px" }}>
                <div style={{ width: "48px", height: "48px", borderRadius: "50%", border: "3px solid var(--blue)", borderTopColor: "transparent", margin: "0 auto 16px", animation: "spin 0.8s linear infinite" }} />
                <p style={{ color: "var(--text-secondary)", fontSize: "16px" }}>Loading analysis report...</p>
              </div>
            </ScrollReveal>
          )}

          {/* Error State */}
          {!isLoading && fetchError && (
            <ScrollReveal variant="fade-up" delay={100}>
              <div style={{ backgroundColor: "white", borderRadius: "16px", padding: "40px", textAlign: "center", border: "1px solid #fecdd3", marginBottom: "32px" }}>
                <p style={{ color: "#dc2626", fontWeight: 600, marginBottom: "8px", fontSize: "18px" }}>Failed to load report</p>
                <p style={{ color: "var(--text-secondary)", marginBottom: "24px", fontSize: "14px" }}>{fetchError}</p>
                <button
                  onClick={handleRetry}
                  className="btn-primary"
                  style={{ padding: "10px 24px" }}
                >
                  Retry
                </button>
              </div>
            </ScrollReveal>
          )}

          {/* Report Content */}
          {!isLoading && report && (
            <>
              {/* Critical Patient Allergy Alert */}
              {matchedAllergies.length > 0 && (
                <ScrollReveal variant="fade-up" delay={75}>
                  <div style={{
                    marginBottom: "28px",
                    padding: "20px 24px",
                    backgroundColor: "var(--red-dim, #fee2e2)",
                    border: "2px solid var(--red, #ef4444)",
                    borderRadius: "16px",
                    boxShadow: "0 4px 14px rgba(239, 68, 68, 0.15)",
                  }}>
                    <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
                      <div style={{
                        width: "40px",
                        height: "40px",
                        backgroundColor: "var(--red, #ef4444)",
                        borderRadius: "10px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                        color: "white"
                      }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                          <line x1="12" y1="9" x2="12" y2="13"></line>
                          <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                      </div>
                      <div>
                        <h3 style={{ fontSize: "17px", fontWeight: "bold", color: "var(--red, #b91c1c)", marginBottom: "6px" }}>
                          CRITICAL PATIENT ALLERGY WARNING
                        </h3>
                        <p style={{ fontSize: "14px", color: "var(--text-primary)", marginBottom: "10px", lineHeight: "1.5" }}>
                          This medicine packaging contains ingredients that match your documented profile allergies:
                        </p>
                        <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "14px", color: "var(--red, #b91c1c)", fontWeight: 600 }}>
                          {matchedAllergies.map((m, idx) => (
                            <li key={idx} style={{ marginBottom: "4px" }}>
                              Detected ingredient <strong>&ldquo;{m.ingredient}&rdquo;</strong> matches your documented allergy to <strong>&ldquo;{m.allergy}&rdquo;</strong>.
                            </li>
                          ))}
                        </ul>
                        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "10px", marginBottom: 0 }}>
                          <strong>Action Required:</strong> Do NOT ingest or administer this medicine without consulting your prescribing healthcare provider or pharmacist.
                        </p>
                      </div>
                    </div>
                  </div>
                </ScrollReveal>
              )}

              <ScrollReveal variant="fade-up" delay={100}>
                <div style={{ marginBottom: "32px" }}>
                  <ProductOverview
                    name={report.product.detected_name}
                    manufacturer={report.product.manufacturer ?? "Unknown Manufacturer"}
                    dosageForm={report.product.dosage_form}
                    confidence={report.confidence.identity_confidence}
                  />
                </div>
              </ScrollReveal>

              {/* Uncertainties Warning */}
              {report.uncertainties && report.uncertainties.length > 0 && (
                <ScrollReveal variant="fade-up" delay={150}>
                  <div style={{ backgroundColor: "#fffbeb", border: "1px solid #fcd34d", borderRadius: "12px", padding: "16px 20px", marginBottom: "24px" }}>
                    <h4 style={{ fontWeight: 700, color: "#92400e", marginBottom: "8px", fontSize: "14px" }}>Uncertainties</h4>
                    <ul style={{ paddingLeft: "20px", margin: 0, color: "#b45309", fontSize: "14px", display: "flex", flexDirection: "column", gap: "4px" }}>
                      {report.uncertainties.map((u, i) => <li key={i}>{u}</li>)}
                    </ul>
                  </div>
                </ScrollReveal>
              )}

              <ScrollReveal variant="fade-up" delay={200}>
                <h2 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "16px" }}>Active Ingredients</h2>
                <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "32px" }}>
                  {report.active_ingredients.map((ingredient, idx) => (
                    <IngredientCard
                      key={idx}
                      canonical_name={ingredient.canonical_name}
                      raw_label_text={ingredient.raw_label_text}
                      strength={ingredient.strength.raw_text}
                      numeric_value={ingredient.strength.numeric_value}
                      unit={ingredient.strength.unit}
                      role={ingredient.role}
                      confidence={ingredient.confidence}
                      explanation={ingredient.explanation}
                      therapeutic_purpose={ingredient.therapeutic_purpose}
                      evidence_sources={ingredient.evidence_sources}
                    />
                  ))}
                </div>
              </ScrollReveal>

              <ScrollReveal variant="fade-up" delay={300}>
                <div style={{ marginBottom: "32px" }}>
                  <ExcipientCollapse ingredients={excipients} />
                </div>
              </ScrollReveal>

              <ScrollReveal variant="fade-up" delay={400}>
                <div style={{ marginBottom: "48px" }}>
                  <SafetyModule profile={report.safety_profile} />
                </div>
              </ScrollReveal>

              {/* Limitations */}
              {report.limitations && report.limitations.length > 0 && (
                <ScrollReveal variant="fade-up" delay={450}>
                  <div style={{ backgroundColor: "var(--surface-alt)", borderRadius: "12px", padding: "16px 20px", marginBottom: "16px" }}>
                    <h4 style={{ fontWeight: 600, color: "var(--text-muted)", marginBottom: "8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Limitations</h4>
                    <ul style={{ paddingLeft: "20px", margin: 0, color: "var(--text-secondary)", fontSize: "13px", display: "flex", flexDirection: "column", gap: "4px" }}>
                      {report.limitations.map((l, i) => <li key={i}>{l}</li>)}
                    </ul>
                  </div>
                </ScrollReveal>
              )}

              <ScrollReveal variant="fade-in" delay={500}>
                <div style={{ backgroundColor: "var(--surface-alt)", borderRadius: "12px", padding: "16px", fontSize: "12px", color: "var(--text-muted)", fontFamily: "monospace", textAlign: "center", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  Audit Hash: {report.audit_hash}
                </div>
              </ScrollReveal>
            </>
          )}

        </div>
      </div>
    </div>
  );
}
