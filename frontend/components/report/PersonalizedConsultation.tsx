"use client";

import React, { useState, useEffect, useCallback } from "react";
import { personalizeAnalysis, PersonalizeResponse } from "@/lib/api";

interface PersonalizedConsultationProps {
  analysisId: string;
  productName: string;
  activeIngredients: string[];
  dosages: string[];
  manufacturer?: string;
}

export default function PersonalizedConsultation({
  analysisId,
  productName,
  activeIngredients,
  dosages,
  manufacturer,
}: PersonalizedConsultationProps) {
  const [allergies, setAllergies] = useState<string[]>([]);
  const [conditions, setConditions] = useState<string[]>([]);
  const [geminiApiKey, setGeminiApiKey] = useState<string>("");

  const [personalization, setPersonalization] = useState<PersonalizeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // In-line key entry for users who want to try BYOK right on the results page
  const [inlineKey, setInlineKey] = useState("");
  const [isSubmittingInlineKey, setIsSubmittingInlineKey] = useState(false);
  const [showInlineKeyInput, setShowInlineKeyInput] = useState(false);

  // Load user profile & trigger analysis
  const fetchPersonalization = useCallback(async (keyOverride?: string) => {
    setIsLoading(true);
    setErrorMsg(null);

    let currentAllergies: string[] = ["Penicillin", "Ibuprofen"];
    let currentConditions: string[] = ["GERD / Acid Reflux"];
    let currentKey = keyOverride !== undefined ? keyOverride : "";

    try {
      const storedAllergies = localStorage.getItem("medlens_user_allergies");
      if (storedAllergies) currentAllergies = JSON.parse(storedAllergies);

      const storedConditions = localStorage.getItem("medlens_user_conditions");
      if (storedConditions) currentConditions = JSON.parse(storedConditions);

      if (keyOverride === undefined) {
        const storedKey = localStorage.getItem("medlens_gemini_api_key");
        if (storedKey) currentKey = storedKey;
      }
    } catch {
      // Fallback
    }

    setAllergies(currentAllergies);
    setConditions(currentConditions);
    setGeminiApiKey(currentKey);

    try {
      const { data, error } = await personalizeAnalysis({
        analysis_id: analysisId,
        product_name: productName,
        active_ingredients: activeIngredients,
        dosages: dosages,
        manufacturer: manufacturer,
        user_allergies: currentAllergies,
        user_conditions: currentConditions,
        gemini_api_key: currentKey || undefined,
      });

      if (error) {
        setErrorMsg(error.message);
      } else if (data) {
        setPersonalization(data);
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Personalization failed");
    } finally {
      setIsLoading(false);
    }
  }, [analysisId, productName, activeIngredients, dosages, manufacturer]);

  useEffect(() => {
    fetchPersonalization();
  }, [fetchPersonalization]);

  const handleApplyInlineKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inlineKey.trim()) return;
    setIsSubmittingInlineKey(true);
    try {
      localStorage.setItem("medlens_gemini_api_key", inlineKey.trim());
      setGeminiApiKey(inlineKey.trim());
      await fetchPersonalization(inlineKey.trim());
      setShowInlineKeyInput(false);
      setInlineKey("");
    } finally {
      setIsSubmittingInlineKey(false);
    }
  };

  const getSafetyBadge = (rating: string) => {
    switch (rating) {
      case "safe":
        return {
          bg: "#ecfdf5",
          border: "#a7f3d0",
          color: "#059669",
          label: "SAFE FOR YOUR PROFILE",
          icon: "✓",
        };
      case "caution":
        return {
          bg: "#fffbeb",
          border: "#fde68a",
          color: "#d97706",
          label: "CLINICAL CAUTION ADVISED",
          icon: "⚠",
        };
      case "high_risk":
      case "contraindicated":
        return {
          bg: "#fef2f2",
          border: "#fecaca",
          color: "#dc2626",
          label: "CONTRAINDICATED / HIGH RISK",
          icon: "✕",
        };
      default:
        return {
          bg: "#f1f5f9",
          border: "#cbd5e1",
          color: "#475569",
          label: "ANALYSIS PENDING",
          icon: "ℹ",
        };
    }
  };

  return (
    <div style={{
      backgroundColor: "white",
      border: "1px solid var(--border)",
      borderRadius: "16px",
      padding: "28px",
      marginBottom: "24px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
    }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
            <h2 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              Personalized Health Consultation
            </h2>
            {personalization?.is_ai_enhanced ? (
              <span style={{
                fontSize: "12px",
                fontWeight: 600,
                padding: "3px 10px",
                borderRadius: "12px",
                background: "linear-gradient(135deg, #eff6ff 0%, #f3e8ff 100%)",
                color: "#7c3aed",
                border: "1px solid #ddd6fe",
                display: "inline-flex",
                alignItems: "center",
                gap: "5px"
              }}>
                <span>✨</span>
                <span>{personalization.model_name || "Google Gemini AI"}</span>
              </span>
            ) : (
              <span style={{
                fontSize: "12px",
                fontWeight: 600,
                padding: "3px 10px",
                borderRadius: "12px",
                backgroundColor: "#f1f5f9",
                color: "#475569",
                border: "1px solid #e2e8f0"
              }}>
                Pharmacopeia Monograph Rules
              </span>
            )}
          </div>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
            Evaluation tailored to your documented allergies ({allergies.length}) and active conditions ({conditions.length}).
          </p>
        </div>

        {personalization && (
          <div style={{
            padding: "8px 16px",
            borderRadius: "10px",
            fontSize: "13px",
            fontWeight: 700,
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            backgroundColor: getSafetyBadge(personalization.overall_safety_rating).bg,
            border: `1px solid ${getSafetyBadge(personalization.overall_safety_rating).border}`,
            color: getSafetyBadge(personalization.overall_safety_rating).color,
            letterSpacing: "0.03em"
          }}>
            <span>{getSafetyBadge(personalization.overall_safety_rating).icon}</span>
            <span>{getSafetyBadge(personalization.overall_safety_rating).label}</span>
          </div>
        )}
      </div>

      {isLoading ? (
        <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)", fontSize: "14px" }}>
          <div style={{
            display: "inline-block",
            width: "28px",
            height: "28px",
            border: "3px solid #e2e8f0",
            borderTopColor: "var(--blue)",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            marginBottom: "10px"
          }}></div>
          <div>Synthesizing personalized health consultation...</div>
        </div>
      ) : errorMsg ? (
        <div style={{ padding: "16px", backgroundColor: "#fef2f2", color: "#dc2626", borderRadius: "8px", fontSize: "14px" }}>
          {errorMsg}
        </div>
      ) : personalization ? (
        <div>
          {/* Executive Summary */}
          <div style={{
            padding: "16px 20px",
            backgroundColor: "#f8fafc",
            borderRadius: "10px",
            borderLeft: "4px solid var(--blue)",
            marginBottom: "24px",
            fontSize: "14.5px",
            lineHeight: "1.6",
            color: "var(--text-primary)"
          }}>
            {personalization.executive_summary}
          </div>

          {/* 2-Column Grid: Allergies & Conditions */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "24px" }} className="mobile-col">
            {/* Allergies Column */}
            <div style={{ border: "1px solid var(--border)", borderRadius: "12px", padding: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <h3 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  Allergy & Excipient Check
                </h3>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  {allergies.join(", ") || "None documented"}
                </span>
              </div>

              {personalization.allergy_matches.length === 0 ? (
                <div style={{ fontSize: "13px", color: "#059669", backgroundColor: "#ecfdf5", padding: "10px", borderRadius: "6px" }}>
                  ✓ No documented allergies conflict with this formulation.
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {personalization.allergy_matches.map((item, idx) => {
                    const isAlert = item.severity === "high" || item.severity === "moderate";
                    return (
                      <div key={idx} style={{
                        padding: "10px 12px",
                        borderRadius: "8px",
                        backgroundColor: isAlert ? "#fef2f2" : "#f8fafc",
                        border: `1px solid ${isAlert ? "#fecaca" : "#e2e8f0"}`,
                        fontSize: "13px"
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                          <span style={{ fontWeight: 600, color: isAlert ? "#dc2626" : "var(--text-primary)" }}>
                            {item.allergen}
                          </span>
                          <span style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            padding: "2px 6px",
                            borderRadius: "4px",
                            backgroundColor: isAlert ? "#fee2e2" : "#e2e8f0",
                            color: isAlert ? "#b91c1c" : "#475569"
                          }}>
                            {item.reaction_type}
                          </span>
                        </div>
                        <p style={{ margin: 0, color: isAlert ? "#991b1b" : "var(--text-secondary)", lineHeight: "1.4" }}>
                          {item.explanation}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Conditions Column */}
            <div style={{ border: "1px solid var(--border)", borderRadius: "12px", padding: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <h3 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  Pre-Existing Condition Compatibility
                </h3>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  {conditions.join(", ") || "None documented"}
                </span>
              </div>

              {personalization.condition_matches.length === 0 ? (
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", backgroundColor: "#f8fafc", padding: "10px", borderRadius: "6px" }}>
                  No pre-existing conditions documented in profile.
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {personalization.condition_matches.map((item, idx) => {
                    let badgeBg = "#f1f5f9";
                    let badgeColor = "#475569";
                    let badgeLabel: string = item.compatibility;

                    if (item.compatibility === "beneficial") {
                      badgeBg = "#ecfdf5";
                      badgeColor = "#059669";
                      badgeLabel = "Therapeutically Indicated";
                    } else if (item.compatibility === "caution") {
                      badgeBg = "#fffbeb";
                      badgeColor = "#d97706";
                      badgeLabel = "Caution Advised";
                    } else if (item.compatibility === "contraindicated") {
                      badgeBg = "#fef2f2";
                      badgeColor = "#dc2626";
                      badgeLabel = "Contraindicated";
                    }

                    return (
                      <div key={idx} style={{
                        padding: "10px 12px",
                        borderRadius: "8px",
                        backgroundColor: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        fontSize: "13px"
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                          <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                            {item.condition}
                          </span>
                          <span style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            padding: "2px 8px",
                            borderRadius: "4px",
                            backgroundColor: badgeBg,
                            color: badgeColor
                          }}>
                            {badgeLabel}
                          </span>
                        </div>
                        <p style={{ margin: 0, color: "var(--text-secondary)", lineHeight: "1.4" }}>
                          {item.clinical_note}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Dosage & Timing Advisory */}
          {personalization.tailored_dosage_advice && (
            <div style={{
              backgroundColor: "#f0fdf4",
              border: "1px solid #bbf7d0",
              borderRadius: "10px",
              padding: "14px 18px",
              marginBottom: "20px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              fontSize: "13.5px",
              color: "#166534"
            }}>
              <span style={{ fontSize: "18px" }}>⏱</span>
              <div>
                <strong>Tailored Timing & Adherence Advice:</strong> {personalization.tailored_dosage_advice}
              </div>
            </div>
          )}

          {/* Precautions & Doctor Questions */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }} className="mobile-col">
            {/* Precautions */}
            <div>
              <h4 style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
                Patient-Specific Precautions
              </h4>
              <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {personalization.personalized_precautions.map((prec, i) => (
                  <li key={i}>{prec}</li>
                ))}
              </ul>
            </div>

            {/* Doctor Questions */}
            <div>
              <h4 style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
                Questions for Your Attending Physician
              </h4>
              <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {personalization.questions_for_doctor.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bring Your Own Key Banner (if not already using Gemini) */}
          {!personalization.is_ai_enhanced && (
            <div style={{
              backgroundColor: "#faf5ff",
              border: "1px dashed #d8b4fe",
              borderRadius: "10px",
              padding: "16px 20px",
              marginTop: "20px",
              fontSize: "13px",
              color: "#581c87"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
                <div>
                  <strong>✨ Unlock AI Clinical Consultation (Optional — Bring Your Own Key):</strong>
                  <p style={{ margin: "2px 0 0 0", color: "#6b21a8" }}>
                    Paste your personal Gemini API key to receive deep neural pharmacology cross-reactivity and contraindication reasoning.
                  </p>
                </div>
                {!showInlineKeyInput ? (
                  <button
                    type="button"
                    onClick={() => setShowInlineKeyInput(true)}
                    style={{
                      backgroundColor: "#7e22ce",
                      color: "white",
                      border: "none",
                      padding: "8px 16px",
                      borderRadius: "6px",
                      fontWeight: 600,
                      cursor: "pointer",
                      fontSize: "13px"
                    }}
                  >
                    Enter Gemini Key
                  </button>
                ) : null}
              </div>

              {showInlineKeyInput && (
                <form onSubmit={handleApplyInlineKey} style={{ marginTop: "14px", display: "flex", gap: "8px", alignItems: "center" }}>
                  <input
                    type="password"
                    placeholder="AIzaSy... (Gemini API Key)"
                    value={inlineKey}
                    onChange={(e) => setInlineKey(e.target.value)}
                    style={{
                      flex: 1,
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid #c084fc",
                      fontSize: "13px",
                      fontFamily: "monospace",
                      outline: "none"
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isSubmittingInlineKey || !inlineKey.trim()}
                    style={{
                      backgroundColor: "#7e22ce",
                      color: "white",
                      border: "none",
                      padding: "8px 16px",
                      borderRadius: "6px",
                      fontWeight: 600,
                      cursor: isSubmittingInlineKey || !inlineKey.trim() ? "not-allowed" : "pointer",
                      fontSize: "13px"
                    }}
                  >
                    {isSubmittingInlineKey ? "Analyzing..." : "Analyze with Gemini"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowInlineKeyInput(false)}
                    style={{
                      backgroundColor: "transparent",
                      color: "#6b21a8",
                      border: "1px solid #d8b4fe",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "13px"
                    }}
                  >
                    Cancel
                  </button>
                </form>
              )}
            </div>
          )}

          <div style={{ marginTop: "16px", fontSize: "11px", color: "var(--text-secondary)", fontStyle: "italic" }}>
            {personalization.disclaimer}
          </div>
        </div>
      ) : null}
    </div>
  );
}
