"use client";

import React, { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import UploadZone from "@/components/scanner/UploadZone";
import ProcessingPulse from "@/components/scanner/ProcessingPulse";
import { ScrollReveal } from "@/components/ScrollReveal";
import Image from "next/image";
import { uploadAnalysis } from "@/lib/api";

export default function ScanPage() {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState(15);
  const [stageMessage, setStageMessage] = useState("Analyzing image clarity & diagnostics...");
  const [isCompleted, setIsCompleted] = useState(false);

  const timerRef = useRef<NodeJS.Timeout[]>([]);

  const clearAllTimers = () => {
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
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
      setStageMessage("Querying openFDA, PubChem & Indian Pharmacopoeia monographs...");
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

  return (
    <div className="flex flex-col font-sans" style={{ minHeight: "100%", backgroundColor: "var(--surface)" }}>
      <div
        style={{
          flex: 1,
          paddingTop: "48px",
          paddingBottom: "96px",
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
            height: "200px",
            background: "linear-gradient(to bottom, rgba(37, 99, 235, 0.03), transparent)",
            zIndex: -10,
            pointerEvents: "none",
          }}
        />

        <ScrollReveal variant="fade-up" style={{ width: "100%", maxWidth: "896px", margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <h1
              style={{
                fontSize: "36px",
                fontWeight: "bold",
                color: "var(--text-primary)",
                letterSpacing: "-0.025em",
                marginBottom: "12px",
                lineHeight: "1.2",
              }}
            >
              Scan Medicine Packaging
            </h1>
            <p
              style={{
                fontSize: "16px",
                color: "var(--text-secondary)",
                maxWidth: "600px",
                margin: "0 auto",
                lineHeight: "1.6",
              }}
            >
              Ensure adequate lighting and position the composition panel clearly. MedLens extracts active chemical
              salts and cross-references them against official pharmacopeias.
            </p>
          </div>

          <div style={{ width: "100%", maxWidth: "672px", margin: "0 auto" }}>
            {!isProcessing ? (
              <UploadZone onFileSelected={handleFileSelected} />
            ) : (
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
