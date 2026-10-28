"use client";

import React, { useState } from "react";
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

  const handleFileSelected = async (file: File) => {
    setUploadError(null);
    setPreviewUrl(URL.createObjectURL(file));
    setIsProcessing(true);

    // Save image preview for results page
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        sessionStorage.setItem("scanned_image", e.target.result as string);
      }
    };
    reader.readAsDataURL(file);

    // Upload to backend
    const { data, error } = await uploadAnalysis(file);

    if (error) {
      setUploadError(error.message);
      setIsProcessing(false);
      return;
    }

    if (data) {
      sessionStorage.setItem("analysis_id", data.analysis_id);
      // Route directly to real persisted analysis record
      router.push(`/dashboard/results/${data.analysis_id}`);
    }
  };

  const handleProcessingComplete = () => {
    // Called by ProcessingPulse animation — routing is already handled above
  };

  return (
    <div className="flex flex-col font-sans" style={{ minHeight: "100%", backgroundColor: "var(--surface)" }}>
      <div style={{ flex: 1, paddingTop: "48px", paddingBottom: "96px", paddingLeft: "24px", paddingRight: "24px", display: "flex", flexDirection: "column", alignItems: "center", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "200px", background: "linear-gradient(to bottom, rgba(37, 99, 235, 0.03), transparent)", zIndex: -10, pointerEvents: "none" }} />

        <ScrollReveal variant="fade-up" style={{ width: "100%", maxWidth: "896px", margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <h1 style={{ fontSize: "36px", fontWeight: "bold", color: "var(--text-primary)", letterSpacing: "-0.025em", marginBottom: "12px", lineHeight: "1.2" }}>
              Scan Medicine Packaging
            </h1>
            <p style={{ fontSize: "16px", color: "var(--text-secondary)", maxWidth: "600px", margin: "0 auto", lineHeight: "1.6" }}>
              Ensure adequate lighting and position the composition panel clearly. MedLens extracts active chemical salts and cross-references them against official pharmacopeias.
            </p>
          </div>

          {uploadError && (
            <div style={{ marginBottom: "24px", padding: "16px", backgroundColor: "var(--red-dim, #fee2e2)", borderLeft: "4px solid var(--red, #ef4444)", borderRadius: "8px", color: "var(--red, #dc2626)" }}>
              <strong>Upload Error:</strong> {uploadError}
            </div>
          )}

          <div style={{ width: "100%", maxWidth: "672px", margin: "0 auto" }}>
            {!isProcessing ? (
              <UploadZone onFileSelected={handleFileSelected} />
            ) : (
              <div className="flex flex-col items-center">
                {previewUrl && (
                  <div className="mb-8 w-48 h-48 relative rounded-xl overflow-hidden border-4 border-white shadow-lg opacity-50 transition-opacity duration-1000">
                    <Image
                      src={previewUrl}
                      alt="Uploaded scan preview"
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-[var(--blue)]/20 mix-blend-overlay"></div>
                    <div className="absolute inset-0 bg-gradient-to-t from-[var(--blue)]/50 to-transparent"></div>
                  </div>
                )}
                <ProcessingPulse onComplete={handleProcessingComplete} />
              </div>
            )}
          </div>
        </ScrollReveal>
      </div>
    </div>
  );
}
