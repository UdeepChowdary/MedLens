"use client";

import React, { useEffect, useState } from "react";
import { IcoCheck, IcoScan, IcoBrain, IcoShield } from "../Icons";

interface ProcessingPulseProps {
  onComplete: () => void;
}

const STAGES = [
  { id: "extract", label: "Extracting Text", icon: IcoScan, duration: 1500 },
  { id: "normalize", label: "Normalizing Ingredients", icon: IcoBrain, duration: 2000 },
  { id: "verify", label: "Verifying Reference Data", icon: IcoShield, duration: 2500 },
  { id: "report", label: "Structuring Report", icon: IcoCheck, duration: 1500 },
];

export default function ProcessingPulse({ onComplete }: ProcessingPulseProps) {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const runStages = () => {
      if (currentStageIndex < STAGES.length) {
        timeoutId = setTimeout(() => {
          if (currentStageIndex === STAGES.length - 1) {
            onComplete();
          } else {
            setCurrentStageIndex((prev) => prev + 1);
          }
        }, STAGES[currentStageIndex].duration);
      }
    };

    runStages();

    return () => clearTimeout(timeoutId);
  }, [currentStageIndex, onComplete]);

  return (
    <div style={{ width: "100%", maxWidth: "512px", margin: "0 auto", padding: "32px", borderRadius: "16px", backgroundColor: "white", boxShadow: "0 20px 25px -5px rgba(37, 99, 235, 0.05), 0 8px 10px -6px rgba(37, 99, 235, 0.05)", border: "1px solid #f1f5f9" }}>
      <div style={{ display: "flex", justifyContent: "center", marginBottom: "32px" }}>
        <div style={{ position: "relative" }}>
          <div style={{ position: "absolute", inset: 0, borderRadius: "50%", backgroundColor: "rgba(37, 99, 235, 0.2)", animation: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite" }}></div>
          <div style={{ position: "relative", backgroundColor: "var(--blue)", padding: "16px", borderRadius: "50%", boxShadow: "0 10px 15px -3px rgba(37, 99, 235, 0.4)" }}>
            <IcoBrain size={32} color="#ffffff" />
          </div>
        </div>
      </div>
      
      <h3 style={{ fontSize: "20px", fontWeight: "bold", textAlign: "center", color: "var(--text-primary)", marginBottom: "32px" }}>
        Analyzing Medicine...
      </h3>
      
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        {STAGES.map((stage, index) => {
          const isPast = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          const Icon = stage.icon;
          
          let iconColor = "#cbd5e1"; // slate-300
          
          if (isPast) {
            iconColor = "#10B981"; // emerald-500
          } else if (isCurrent) {
            iconColor = "var(--blue)";
          }

          return (
            <div key={stage.id} style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <div 
                style={{ 
                  width: "40px", height: "40px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", border: "2px solid", transition: "colors 500ms",
                  borderColor: isPast ? "#10B981" : isCurrent ? "var(--blue)" : "#e2e8f0",
                  backgroundColor: isPast ? "#ecfdf5" : isCurrent ? "#eff6ff" : "transparent"
                }}
              >
                {isPast ? <IcoCheck size={18} color={iconColor} /> : <Icon size={18} color={iconColor} />}
              </div>
              
              <div style={{ flex: 1 }}>
                <p style={{ transition: "colors 500ms", color: isPast ? "#10B981" : isCurrent ? "var(--blue)" : "#cbd5e1", fontWeight: isCurrent ? 500 : 400 }}>
                  {stage.label}
                </p>
                {isCurrent && (
                  <div className="w-full bg-slate-100 h-1.5 mt-2 rounded-sm overflow-hidden">
                    <div className="h-full bg-[var(--blue)] rounded-sm animate-pulse w-full origin-left" style={{ animationDuration: "1s" }}></div>
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
