"use client";

import React from "react";
import { IcoCheck, IcoScan, IcoBrain, IcoShield, IcoFile, IcoX } from "../Icons";

export interface PipelineStage {
  id: string;
  label: string;
  detail: string;
  icon: React.ComponentType<{ size?: number; color?: string }>;
}

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: "diagnostics",
    label: "Image Clarity & Diagnostics",
    detail: "Laplacian blur variance check (σ² ≥ 100), EXIF auto-rotation & SHA-256 digest",
    icon: IcoScan,
  },
  {
    id: "ocr",
    label: "Packaging Text OCR Extraction",
    detail: "Executing pluggable OCR dispatcher for typography & composition panel",
    icon: IcoFile,
  },
  {
    id: "normalize",
    label: "Chemical Salt & INN Normalization",
    detail: "Mapping detected pharmaceutical salts to 3-tier canonical INN registry",
    icon: IcoBrain,
  },
  {
    id: "verify",
    label: "Pharmacopeial & Monograph Grounding",
    detail: "Cross-referencing openFDA labels, PubChem CIDs & Indian Pharmacopoeia standards",
    icon: IcoShield,
  },
  {
    id: "report",
    label: "Verification Report Generation",
    detail: "Computing multidimensional confidence dimensions & audit trail",
    icon: IcoCheck,
  },
];

interface ProcessingPulseProps {
  currentStageIndex: number;
  progressPercent: number;
  stageMessage?: string;
  isCompleted?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export default function ProcessingPulse({
  currentStageIndex,
  progressPercent,
  stageMessage,
  isCompleted = false,
  error = null,
  onRetry,
}: ProcessingPulseProps) {
  return (
    <div
      style={{
        width: "100%",
        maxWidth: "580px",
        margin: "0 auto",
        padding: "32px",
        borderRadius: "16px",
        backgroundColor: "white",
        boxShadow: "0 20px 25px -5px rgba(37, 99, 235, 0.05), 0 8px 10px -6px rgba(37, 99, 235, 0.05)",
        border: "1px solid #e2e8f0",
      }}
    >
      {/* Top Status Icon & Pulse */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: "24px" }}>
        <div style={{ position: "relative" }}>
          {!error && !isCompleted && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: "50%",
                backgroundColor: "rgba(37, 99, 235, 0.2)",
                animation: "ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite",
              }}
            />
          )}
          <div
            style={{
              position: "relative",
              backgroundColor: error ? "#dc2626" : isCompleted ? "#10b981" : "var(--blue, #2563eb)",
              padding: "16px",
              borderRadius: "50%",
              boxShadow: error
                ? "0 10px 15px -3px rgba(220, 38, 38, 0.4)"
                : isCompleted
                ? "0 10px 15px -3px rgba(16, 185, 129, 0.4)"
                : "0 10px 15px -3px rgba(37, 99, 235, 0.4)",
              transition: "all 400ms ease",
            }}
          >
            {error ? (
              <IcoX size={32} />
            ) : isCompleted ? (
              <IcoCheck size={32} color="#ffffff" />
            ) : (
              <IcoBrain size={32} color="#ffffff" />
            )}
          </div>
        </div>
      </div>

      {/* Header & Subtitle */}
      <div style={{ textAlign: "center", marginBottom: "24px" }}>
        <h3
          style={{
            fontSize: "20px",
            fontWeight: "bold",
            color: error ? "#dc2626" : "var(--text-primary, #0f172a)",
            marginBottom: "6px",
          }}
        >
          {error
            ? "Analysis Pipeline Interrupted"
            : isCompleted
            ? "Verification Report Ready!"
            : "Analyzing Medicine Composition..."}
        </h3>
        <p style={{ fontSize: "14px", color: "var(--text-secondary, #64748b)" }}>
          {error
            ? "An error occurred during verification. Review the diagnosis below."
            : stageMessage || "Deterministic extraction and verification in progress"}
        </p>
      </div>

      {/* Overall Progress Bar */}
      {!error && (
        <div style={{ marginBottom: "28px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "12px",
              fontWeight: 600,
              color: "var(--text-secondary, #64748b)",
              marginBottom: "8px",
            }}
          >
            <span>Pipeline Progress</span>
            <span>{Math.min(100, Math.round(progressPercent))}%</span>
          </div>
          <div
            style={{
              width: "100%",
              height: "8px",
              backgroundColor: "#f1f5f9",
              borderRadius: "9999px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${Math.min(100, progressPercent)}%`,
                height: "100%",
                backgroundColor: isCompleted ? "#10b981" : "var(--blue, #2563eb)",
                borderRadius: "9999px",
                transition: "width 400ms ease, background-color 400ms ease",
              }}
            />
          </div>
        </div>
      )}

      {/* Error Card */}
      {error && (
        <div
          style={{
            marginBottom: "24px",
            padding: "16px",
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: "8px",
            color: "#991b1b",
            fontSize: "14px",
            lineHeight: 1.5,
          }}
        >
          <strong>Diagnostic Error:</strong> {error}
          {onRetry && (
            <div style={{ marginTop: "12px" }}>
              <button
                type="button"
                onClick={onRetry}
                style={{
                  padding: "8px 16px",
                  fontSize: "13px",
                  fontWeight: 600,
                  backgroundColor: "#dc2626",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                Scan Another Image
              </button>
            </div>
          )}
        </div>
      )}

      {/* Pipeline Stage List */}
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {PIPELINE_STAGES.map((stage, index) => {
          const isPast = isCompleted || index < currentStageIndex;
          const isCurrent = !isCompleted && index === currentStageIndex;
          const isPending = !isCompleted && index > currentStageIndex;
          const Icon = stage.icon;

          let iconColor = "#94a3b8";
          if (isPast) iconColor = "#10b981";
          else if (isCurrent) iconColor = "var(--blue, #2563eb)";

          return (
            <div
              key={stage.id}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "16px",
                opacity: isPending ? 0.45 : 1,
                transition: "opacity 300ms ease",
              }}
            >
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "2px solid",
                  borderColor: isPast ? "#10b981" : isCurrent ? "var(--blue, #2563eb)" : "#cbd5e1",
                  backgroundColor: isPast ? "#ecfdf5" : isCurrent ? "#eff6ff" : "transparent",
                  flexShrink: 0,
                  transition: "all 300ms ease",
                }}
              >
                {isPast ? <IcoCheck size={18} color="#10b981" /> : <Icon size={18} color={iconColor} />}
              </div>

              <div style={{ flex: 1 }}>
                <p
                  style={{
                    fontSize: "14px",
                    fontWeight: isCurrent ? 600 : 500,
                    color: isPast
                      ? "#0f172a"
                      : isCurrent
                      ? "var(--blue, #2563eb)"
                      : "var(--text-secondary, #64748b)",
                    marginBottom: "2px",
                  }}
                >
                  {stage.label}
                </p>
                <p style={{ fontSize: "12px", color: "var(--text-muted, #94a3b8)", lineHeight: 1.4 }}>
                  {stage.detail}
                </p>

                {isCurrent && !error && (
                  <div
                    style={{
                      width: "100%",
                      height: "3px",
                      backgroundColor: "#eff6ff",
                      borderRadius: "2px",
                      overflow: "hidden",
                      marginTop: "6px",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        backgroundColor: "var(--blue, #2563eb)",
                        borderRadius: "2px",
                        animation: "pulse 1s infinite",
                        width: "100%",
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
