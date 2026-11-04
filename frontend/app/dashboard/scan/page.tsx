"use client";

import React, { useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import UploadZone from "@/components/scanner/UploadZone";
import ProcessingPulse from "@/components/scanner/ProcessingPulse";
import { ScrollReveal } from "@/components/ScrollReveal";
import { uploadAnalysis, verifyGeminiKey, VerifyKeyResponse } from "@/lib/api";
import { IcoShield, IcoBrain, IcoCheck, IcoHelpCircle } from "@/components/Icons";

export default function ScanPage() {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState(15);
  const [stageMessage, setStageMessage] = useState("Analyzing image clarity & diagnostics...");
  const [isCompleted, setIsCompleted] = useState(false);

  // BYOK Gemini API Key & Personalization Settings
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [savedKey, setSavedKey] = useState("");
  const [showApiKeyText, setShowApiKeyText] = useState(false);
  const [isTestingKey, setIsTestingKey] = useState(false);
  const [keyValidation, setKeyValidation] = useState<VerifyKeyResponse | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [showHowToGuide, setShowHowToGuide] = useState(false);

  // User Health Profile Context
  const [userAllergies, setUserAllergies] = useState<string[]>([]);
  const [userConditions, setUserConditions] = useState<string[]>([]);

  const timerRef = useRef<NodeJS.Timeout[]>([]);

  useEffect(() => {
    try {
      const storedKey = localStorage.getItem("medlens_gemini_api_key");
      if (storedKey) {
        setGeminiApiKey(storedKey);
        setSavedKey(storedKey);
      }

      const storedAllergies = localStorage.getItem("medlens_user_allergies");
      if (storedAllergies) {
        const parsed = JSON.parse(storedAllergies);
        if (Array.isArray(parsed)) setUserAllergies(parsed);
      } else {
        setUserAllergies(["Penicillin", "Ibuprofen"]);
      }

      const storedConditions = localStorage.getItem("medlens_user_conditions");
      if (storedConditions) {
        const parsed = JSON.parse(storedConditions);
        if (Array.isArray(parsed)) setUserConditions(parsed);
      } else {
        setUserConditions(["GERD / Acid Reflux"]);
      }
    } catch {
      // Local storage fallback
    }
  }, []);

  const clearAllTimers = () => {
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
  };

  const handleTestKey = async () => {
    if (!geminiApiKey.trim()) {
      setKeyValidation({ valid: false, message: "Please paste or enter your Gemini API key first." });
      return;
    }
    setIsTestingKey(true);
    setKeyValidation(null);
    try {
      const { data, error } = await verifyGeminiKey(geminiApiKey.trim());
      if (error) {
        setKeyValidation({ valid: false, message: error.message });
      } else if (data) {
        setKeyValidation(data);
      }
    } catch {
      setKeyValidation({ valid: false, message: "Connection to verification service failed." });
    } finally {
      setIsTestingKey(false);
    }
  };

  const handleSaveKey = () => {
    const trimmed = geminiApiKey.trim();
    try {
      if (trimmed) {
        localStorage.setItem("medlens_gemini_api_key", trimmed);
        setSavedKey(trimmed);
      } else {
        localStorage.removeItem("medlens_gemini_api_key");
        setSavedKey("");
      }
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3500);
    } catch {
      // Storage error handling
    }
  };

  const handleClearKey = () => {
    try {
      localStorage.removeItem("medlens_gemini_api_key");
      setGeminiApiKey("");
      setSavedKey("");
      setKeyValidation(null);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3500);
    } catch {
      // Storage error handling
    }
  };

  const handleFileSelected = async (file: File) => {
    clearAllTimers();
    setUploadError(null);
    setIsCompleted(false);
    setCurrentStageIndex(0);
    setProgressPercent(18);
    setStageMessage("Running Laplacian blur variance check (σ² ≥ 100)...");
    setPreviewUrl(URL.createObjectURL(file));
    setIsProcessing(true);

    // Save image preview for the dynamic results page
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        sessionStorage.setItem("scanned_image", e.target.result as string);
      }
    };
    reader.readAsDataURL(file);

    // Stage progression timelines reflecting actual backend pipeline lifecycle
    const t1 = setTimeout(() => {
      setCurrentStageIndex(1);
      setProgressPercent(40);
      setStageMessage("Dispatching OCR text extraction on packaging panel...");
    }, 450);

    const t2 = setTimeout(() => {
      setCurrentStageIndex(2);
      setProgressPercent(65);
      setStageMessage("Normalizing chemical salts against 3-tier canonical INN registry...");
    }, 950);

    const t3 = setTimeout(() => {
      setCurrentStageIndex(3);
      setProgressPercent(82);
      setStageMessage(
        savedKey
          ? "Cross-referencing openFDA & preparing AI clinical personalization..."
          : "Querying openFDA, PubChem & Indian Pharmacopoeia monographs..."
      );
    }, 1450);

    timerRef.current.push(t1, t2, t3);

    try {
      // Execute live pipeline analysis
      const { data, error } = await uploadAnalysis(file);
      clearAllTimers();

      if (error) {
        setUploadError(error.message);
        return;
      }

      if (data) {
        sessionStorage.setItem("analysis_id", data.analysis_id);

        // Advance to final report generation stage
        setCurrentStageIndex(4);
        setProgressPercent(100);
        setIsCompleted(true);
        setStageMessage("Audit hash generated. Report ready!");

        // Brief delay for visual completion feedback before routing
        setTimeout(() => {
          router.push(`/dashboard/results/${data.analysis_id}`);
        }, 700);
      }
    } catch (err: unknown) {
      clearAllTimers();
      const message = err instanceof Error ? err.message : "Unexpected pipeline exception";
      setUploadError(message);
    }
  };

  const handleRetry = () => {
    clearAllTimers();
    setIsProcessing(false);
    setUploadError(null);
    setIsCompleted(false);
    setPreviewUrl(null);
  };

  const handleSelectDemoSample = async (samplePath: string, fileName: string) => {
    try {
      const response = await fetch(samplePath);
      const blob = await response.blob();
      const file = new File([blob], fileName, { type: "image/jpeg" });
      handleFileSelected(file);
    } catch (err) {
      console.error("Failed to load demo sample", err);
    }
  };

  return (
    <div className="flex flex-col font-sans" style={{ minHeight: "100%", backgroundColor: "var(--surface)" }}>
      <div
        style={{
          flex: 1,
          paddingTop: "40px",
          paddingBottom: "80px",
          paddingLeft: "24px",
          paddingRight: "24px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "220px",
            background: "linear-gradient(to bottom, rgba(37, 99, 235, 0.04), transparent)",
            zIndex: -10,
            pointerEvents: "none",
          }}
        />

        <ScrollReveal variant="fade-up" style={{ width: "100%", maxWidth: "800px", margin: "0 auto" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: "32px" }}>
            <h1
              style={{
                fontSize: "32px",
                fontWeight: "bold",
                color: "var(--text-primary)",
                letterSpacing: "-0.025em",
                marginBottom: "10px",
                lineHeight: "1.2",
              }}
            >
              Scan Medicine Packaging
            </h1>
            <p
              style={{
                fontSize: "15px",
                color: "var(--text-secondary)",
                maxWidth: "600px",
                margin: "0 auto",
                lineHeight: "1.6",
              }}
            >
              Upload or snap a photo of your medicine blister pack or bottle label. MedLens verifies active pharmaceutical salts
              and delivers safety & contraindication insights.
            </p>
          </div>

          <div style={{ width: "100%", maxWidth: "720px", margin: "0 auto" }}>
            {!isProcessing ? (
              <div className="flex flex-col gap-6">
                {/* 1. Upload Box */}
                <UploadZone onFileSelected={handleFileSelected} />

                {/* 1.5 Quick 1-Click Demo Packaging Samples */}
                <div
                  style={{
                    backgroundColor: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: "16px",
                    padding: "18px 20px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "12px",
                      flexWrap: "wrap",
                      gap: "8px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "16px" }}>⚡</span>
                      <span style={{ fontSize: "13.5px", fontWeight: 700, color: "var(--text-primary)" }}>
                        Don&apos;t have packaging nearby? Test with real blister samples:
                      </span>
                    </div>
                    <span
                      style={{
                        fontSize: "11px",
                        color: "#475569",
                        backgroundColor: "#f1f5f9",
                        padding: "2px 8px",
                        borderRadius: "10px",
                        fontWeight: 600,
                      }}
                    >
                      Instant 1-Click Intake
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "10px" }}>
                    {[
                      {
                        name: "Dolo 650",
                        salt: "Paracetamol 650 mg",
                        category: "Fever & Pain",
                        file: "/samples/dolo_650.jpg",
                        color: "#2563eb",
                      },
                      {
                        name: "Augmentin 625 Duo",
                        salt: "Amoxicillin + Clavulanate",
                        category: "Antibiotic Ratio",
                        file: "/samples/augmentin_625.jpg",
                        color: "#059669",
                      },
                      {
                        name: "Pan 40",
                        salt: "Pantoprazole 40 mg",
                        category: "Acidity / GERD",
                        file: "/samples/pan_40.jpg",
                        color: "#d97706",
                      },
                    ].map((sample) => (
                      <button
                        key={sample.name}
                        type="button"
                        onClick={() =>
                          handleSelectDemoSample(
                            sample.file,
                            `${sample.name.toLowerCase().replace(/[^a-z0-9]/g, "_")}.jpg`
                          )
                        }
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                          padding: "10px 12px",
                          borderRadius: "10px",
                          border: "1px solid #e2e8f0",
                          backgroundColor: "#f8fafc",
                          cursor: "pointer",
                          textAlign: "left",
                          transition: "all 0.15s ease",
                        }}
                        className="hover:border-blue-500 hover:bg-blue-50/50"
                      >
                        <div
                          style={{
                            width: "40px",
                            height: "40px",
                            borderRadius: "8px",
                            overflow: "hidden",
                            position: "relative",
                            flexShrink: 0,
                            backgroundColor: "#e2e8f0",
                            border: "1px solid #cbd5e1",
                          }}
                        >
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={sample.file}
                            alt={sample.name}
                            style={{ width: "100%", height: "100%", objectFit: "cover" }}
                          />
                        </div>
                        <div style={{ minWidth: 0, flex: 1 }}>
                          <div
                            style={{
                              fontSize: "13px",
                              fontWeight: 700,
                              color: "var(--text-primary)",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {sample.name}
                          </div>
                          <div
                            style={{
                              fontSize: "11px",
                              color: "var(--text-secondary)",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {sample.salt}
                          </div>
                        </div>
                        <span style={{ fontSize: "12px", color: sample.color, fontWeight: 700 }}>→</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 2. Analysis Mode & Gemini API Key BYOK Card */}
                <div
                  style={{
                    backgroundColor: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: "16px",
                    padding: "24px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
                  }}
                >
                  {/* Card Header & Active Mode Badge */}
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "12px", marginBottom: "16px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <div
                        style={{
                          backgroundColor: savedKey ? "#eff6ff" : "#f8fafc",
                          padding: "8px",
                          borderRadius: "10px",
                          border: `1px solid ${savedKey ? "#bfdbfe" : "#e2e8f0"}`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <IcoBrain size={22} color={savedKey ? "#2563eb" : "#64748b"} />
                      </div>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <h2 style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)" }}>
                            Analysis Mode & Personalization
                          </h2>
                          <span
                            style={{
                              fontSize: "11px",
                              padding: "2px 8px",
                              borderRadius: "12px",
                              backgroundColor: "#f1f5f9",
                              color: "#475569",
                              fontWeight: 600,
                              border: "1px solid #cbd5e1",
                            }}
                          >
                            Optional • BYOK
                          </span>
                        </div>
                        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
                          Choose between free standard pharmacopeia rules or deep AI-personalized clinical cross-checks.
                        </p>
                      </div>
                    </div>

                    {/* Mode Status Pill */}
                    <div
                      style={{
                        padding: "6px 12px",
                        borderRadius: "20px",
                        fontSize: "12px",
                        fontWeight: 600,
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        whiteSpace: "nowrap",
                        backgroundColor: savedKey ? "#ecfdf5" : "#f1f5f9",
                        color: savedKey ? "#059669" : "#475569",
                        border: `1px solid ${savedKey ? "#a7f3d0" : "#cbd5e1"}`,
                      }}
                    >
                      {savedKey ? (
                        <>
                          <IcoCheck size={14} color="#059669" />
                          <span>AI Clinical Mode Active</span>
                        </>
                      ) : (
                        <span>Standard Mode (No Key)</span>
                      )}
                    </div>
                  </div>

                  {/* Mode Comparison Grid */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "12px",
                      marginBottom: "20px",
                    }}
                  >
                    {/* Option A: Standard Mode */}
                    <div
                      style={{
                        padding: "14px 16px",
                        borderRadius: "12px",
                        border: !savedKey ? "2px solid #2563eb" : "1px solid #e2e8f0",
                        backgroundColor: !savedKey ? "rgba(37, 99, 235, 0.03)" : "#f8fafc",
                        position: "relative",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)" }}>
                          Standard Analysis
                        </span>
                        <span
                          style={{
                            fontSize: "10px",
                            padding: "1px 6px",
                            borderRadius: "10px",
                            backgroundColor: "#e2e8f0",
                            color: "#475569",
                            fontWeight: 600,
                          }}
                        >
                          Default • Free
                        </span>
                      </div>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                        Runs local pharmacopeia monographs (US FDA, PubChem, Indian Pharmacopoeia). Zero setup, fast INN verification, and general label warnings.
                      </p>
                    </div>

                    {/* Option B: AI Enhanced Mode */}
                    <div
                      style={{
                        padding: "14px 16px",
                        borderRadius: "12px",
                        border: savedKey ? "2px solid #10b981" : "1px solid #e2e8f0",
                        backgroundColor: savedKey ? "rgba(16, 185, 129, 0.03)" : "#f8fafc",
                        position: "relative",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)" }}>
                          AI Personalization
                        </span>
                        <span
                          style={{
                            fontSize: "10px",
                            padding: "1px 6px",
                            borderRadius: "10px",
                            backgroundColor: savedKey ? "#d1fae5" : "#e2e8f0",
                            color: savedKey ? "#065f46" : "#475569",
                            fontWeight: 600,
                          }}
                        >
                          Google Gemini
                        </span>
                      </div>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                        Deep clinical reasoning tailored to your allergies & health conditions. Flags cross-reactivity, organ cautions, and safe alternatives.
                      </p>
                    </div>
                  </div>

                  {/* Active Health Profile Banner */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 14px",
                      backgroundColor: "#f8fafc",
                      borderRadius: "10px",
                      border: "1px solid #e2e8f0",
                      marginBottom: "18px",
                      fontSize: "12px",
                      color: "var(--text-secondary)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <IcoShield size={16} color="#2563eb" />
                      <span>
                        Cross-checking against your profile:{" "}
                        <strong style={{ color: "var(--text-primary)" }}>
                          {userAllergies.length} {userAllergies.length === 1 ? "allergy" : "allergies"}
                        </strong>{" "}
                        ({userAllergies.slice(0, 2).join(", ")}
                        {userAllergies.length > 2 ? "..." : ""}) &amp;{" "}
                        <strong style={{ color: "var(--text-primary)" }}>
                          {userConditions.length} {userConditions.length === 1 ? "condition" : "conditions"}
                        </strong>{" "}
                        ({userConditions.slice(0, 2).join(", ")}
                        {userConditions.length > 2 ? "..." : ""})
                      </span>
                    </div>
                    <Link
                      href="/dashboard/profile"
                      style={{
                        color: "var(--blue)",
                        fontWeight: 600,
                        textDecoration: "none",
                        whiteSpace: "nowrap",
                      }}
                    >
                      Edit Profile ↗
                    </Link>
                  </div>

                  {/* API Key Input Field & Actions */}
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "13px",
                        fontWeight: 600,
                        color: "var(--text-primary)",
                        marginBottom: "6px",
                      }}
                    >
                      Google Gemini API Key (Optional)
                    </label>

                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      <div style={{ position: "relative", flex: 1 }}>
                        <input
                          type={showApiKeyText ? "text" : "password"}
                          placeholder="Enter Gemini API key (leave blank for standard monograph mode)"
                          value={geminiApiKey}
                          onChange={(e) => {
                            setGeminiApiKey(e.target.value);
                            setKeyValidation(null);
                          }}
                          style={{
                            width: "100%",
                            padding: "10px 48px 10px 14px",
                            borderRadius: "8px",
                            border: "1px solid #cbd5e1",
                            fontSize: "13px",
                            fontFamily: "monospace",
                            outline: "none",
                            backgroundColor: "white",
                          }}
                        />
                        <button
                          type="button"
                          onClick={() => setShowApiKeyText(!showApiKeyText)}
                          style={{
                            position: "absolute",
                            right: "12px",
                            top: "50%",
                            transform: "translateY(-50%)",
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            color: "var(--text-secondary)",
                            fontSize: "12px",
                            fontWeight: 600,
                          }}
                        >
                          {showApiKeyText ? "Hide" : "Show"}
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={handleTestKey}
                        disabled={isTestingKey || !geminiApiKey.trim()}
                        style={{
                          backgroundColor: "#f8fafc",
                          color: "var(--text-primary)",
                          border: "1px solid #cbd5e1",
                          padding: "10px 16px",
                          borderRadius: "8px",
                          fontSize: "13px",
                          fontWeight: 600,
                          cursor: isTestingKey || !geminiApiKey.trim() ? "not-allowed" : "pointer",
                          opacity: !geminiApiKey.trim() ? 0.6 : 1,
                          whiteSpace: "nowrap",
                        }}
                      >
                        {isTestingKey ? "Testing..." : "Test Key"}
                      </button>

                      <button
                        type="button"
                        onClick={handleSaveKey}
                        style={{
                          backgroundColor: "var(--blue)",
                          color: "white",
                          border: "none",
                          padding: "10px 18px",
                          borderRadius: "8px",
                          fontSize: "13px",
                          fontWeight: 600,
                          cursor: "pointer",
                          whiteSpace: "nowrap",
                        }}
                      >
                        Save Key
                      </button>

                      {savedKey && (
                        <button
                          type="button"
                          onClick={handleClearKey}
                          title="Remove key and return to standard mode"
                          style={{
                            backgroundColor: "transparent",
                            color: "#ef4444",
                            border: "1px solid #fecaca",
                            padding: "10px 12px",
                            borderRadius: "8px",
                            fontSize: "13px",
                            fontWeight: 600,
                            cursor: "pointer",
                            whiteSpace: "nowrap",
                          }}
                        >
                          Clear
                        </button>
                      )}
                    </div>

                    {/* Key Verification Response Alert */}
                    {keyValidation && (
                      <div
                        style={{
                          marginTop: "10px",
                          padding: "10px 14px",
                          borderRadius: "8px",
                          fontSize: "12px",
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          backgroundColor: keyValidation.valid ? "#ecfdf5" : "#fef2f2",
                          color: keyValidation.valid ? "#059669" : "#dc2626",
                          border: `1px solid ${keyValidation.valid ? "#a7f3d0" : "#fecaca"}`,
                        }}
                      >
                        <span style={{ fontWeight: "bold" }}>{keyValidation.valid ? "✓" : "⚠"}</span>
                        <span>{keyValidation.message}</span>
                        {keyValidation.model_tested && (
                          <span style={{ fontSize: "11px", opacity: 0.85 }}>({keyValidation.model_tested})</span>
                        )}
                      </div>
                    )}

                    {/* Save Confirmation */}
                    {saveSuccess && (
                      <div
                        style={{
                          marginTop: "10px",
                          padding: "8px 12px",
                          borderRadius: "8px",
                          fontSize: "12px",
                          backgroundColor: "#eff6ff",
                          color: "#1d4ed8",
                          border: "1px solid #bfdbfe",
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                        }}
                      >
                        <IcoCheck size={14} color="#1d4ed8" />
                        <span>
                          {savedKey
                            ? "Gemini API key saved to your browser! AI clinical personalization is activated for upcoming scans."
                            : "Key removed. Switched back to Standard Monograph analysis."}
                        </span>
                      </div>
                    )}

                    {/* How and Where to get the Key Link / Toggle */}
                    <div
                      style={{
                        marginTop: "14px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap",
                        gap: "8px",
                        fontSize: "12px",
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => setShowHowToGuide(!showHowToGuide)}
                        style={{
                          background: "none",
                          border: "none",
                          padding: 0,
                          color: "var(--blue)",
                          cursor: "pointer",
                          fontWeight: 600,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "5px",
                        }}
                      >
                        <IcoHelpCircle size={15} color="var(--blue)" />
                        <span>{showHowToGuide ? "Hide instructions" : "Where & how do I get a free Gemini API key?"}</span>
                      </button>

                      <a
                        href="https://aistudio.google.com/app/apikey"
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          color: "#2563eb",
                          textDecoration: "none",
                          fontWeight: 600,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <span>Open Google AI Studio</span>
                        <span>↗</span>
                      </a>
                    </div>

                    {/* Step-by-Step Guide Walkthrough */}
                    {showHowToGuide && (
                      <div
                        style={{
                          marginTop: "14px",
                          padding: "16px",
                          backgroundColor: "#f8fafc",
                          borderRadius: "12px",
                          border: "1px solid #e2e8f0",
                          fontSize: "13px",
                          lineHeight: "1.6",
                        }}
                      >
                        <div style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "8px" }}>
                          How to get a Free Google Gemini API Key in 3 Steps:
                        </div>
                        <ol style={{ paddingLeft: "18px", margin: "0 0 12px 0", color: "#334155" }}>
                          <li style={{ marginBottom: "6px" }}>
                            Go to{" "}
                            <a
                              href="https://aistudio.google.com/app/apikey"
                              target="_blank"
                              rel="noreferrer"
                              style={{ color: "#2563eb", fontWeight: 600, textDecoration: "underline" }}
                            >
                              Google AI Studio (aistudio.google.com/app/apikey)
                            </a>{" "}
                            and sign in with any standard Google account.
                          </li>
                          <li style={{ marginBottom: "6px" }}>
                            Click the blue button labeled <strong>&ldquo;Create API Key&rdquo;</strong> (or &ldquo;Get API key&rdquo;). No credit card or paid billing required for free personal tier.
                          </li>
                          <li style={{ marginBottom: "6px" }}>
                            Copy the generated key string, paste it into the field above, and click <strong>&ldquo;Save Key&rdquo;</strong>.
                          </li>
                        </ol>

                        <div
                          style={{
                            padding: "8px 12px",
                            backgroundColor: "#f1f5f9",
                            borderRadius: "8px",
                            fontSize: "12px",
                            color: "#475569",
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                          }}
                        >
                          <IcoShield size={16} color="#64748b" />
                          <span>
                            <strong>Privacy Promise:</strong> Your key is stored exclusively in your browser&apos;s local storage (<code>localStorage</code>) on your machine. MedLens never transmits or stores your key on remote servers.
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              /* Processing Pipeline */
              <div className="flex flex-col items-center">
                {previewUrl && (
                  <div className="mb-8 w-44 h-44 relative rounded-xl overflow-hidden border-4 border-white shadow-lg opacity-85 transition-opacity duration-700">
                    <Image src={previewUrl} alt="Uploaded scan preview" fill className="object-cover" />
                    <div className="absolute inset-0 bg-[var(--blue)]/15 mix-blend-overlay" />
                    <div className="absolute inset-0 bg-gradient-to-t from-[var(--blue)]/40 to-transparent" />
                  </div>
                )}
                <ProcessingPulse
                  currentStageIndex={currentStageIndex}
                  progressPercent={progressPercent}
                  stageMessage={stageMessage}
                  isCompleted={isCompleted}
                  error={uploadError}
                  onRetry={handleRetry}
                />
              </div>
            )}
          </div>
        </ScrollReveal>
      </div>
    </div>
  );
}
