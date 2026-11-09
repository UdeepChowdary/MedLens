"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAccessibility, FontSizeOption, ContrastOption } from "@/context/AccessibilityContext";

export default function AccessibilityToolbar() {
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  const {
    fontSize,
    contrastMode,
    dyslexicFont,
    reducedMotion,
    speechLang,
    speechRate,
    setFontSize,
    setContrastMode,
    setDyslexicFont,
    setReducedMotion,
    setSpeechLang,
    setSpeechRate,
    speak,
    stopSpeaking,
    isSpeaking,
    hasNativeVoice,
    activeVoiceName,
    resetDefaults,
  } = useAccessibility();

  // Keyboard shortcut: Alt + A or Option + A toggles accessibility panel
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && (e.key === "a" || e.key === "A")) {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  const testVoiceSample = () => {
    const isNative = hasNativeVoice(speechLang);
    let sampleText = "";

    if (speechLang.startsWith("hi")) {
      sampleText = isNative
        ? "मेडलेंस सक्रिय दवा सत्यापित: पैरासिटामोल ६५० मिलीग्राम। बुखार और दर्द में राहत के लिए सुरक्षित।"
        : "MedLens verified medicine: Paracetamol 650 milligram. Yeh dawai bukhar aur dard mein aaram ke liye surakshit hai.";
    } else if (speechLang.startsWith("te")) {
      sampleText = isNative
        ? "మెడ్‌లెన్స్ ఔషధ ధృవీకరణ: పారాసిటమాల్ 650 మిల్లీగ్రాములు. జ్వరం మరియు నొప్పి నివారణకు సిఫార్సు చేయబడింది."
        : "MedLens verified medicine: Paracetamol 650 milligram. Ee mandhu jvaram mariyu noppi thagginchataniki upayogapaduthundhi.";
    } else if (speechLang.startsWith("ta")) {
      sampleText = isNative
        ? "மெட்லென்ஸ் மருந்து சரிபார்ப்பு: பாராசிட்டமால் 650 மில்லிகிராம். காய்ச்சல் மற்றும் வலி நிவாரணத்திற்கு பாதுகாப்பானது."
        : "MedLens verified medicine: Paracetamol 650 milligram. Indha marundhu kaichal matrum valiyai kuraikka payanpadugiradhu.";
    } else if (speechLang.startsWith("es")) {
      sampleText = "MedLens medicamento verificado: Paracetamol 650 miligramos. Seguro para la fiebre y el alivio del dolor.";
    } else {
      sampleText = "MedLens active salt verified: Paracetamol 650 milligrams. Safe for fever and pain relief.";
    }

    speak(sampleText, undefined, speechLang);
  };

  const isNative = hasNativeVoice(speechLang);

  return (
    <>
      {/* Floating Accessibility Trigger Button (Bottom-Left) */}
      <div style={{ position: "fixed", bottom: "24px", left: "24px", zIndex: 9980 }}>
        <button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          aria-haspopup="dialog"
          aria-label="Open Accessibility & Voice Settings (Shortcut: Alt + A)"
          title="Accessibility & Voice Settings (Alt + A)"
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "50%",
            backgroundColor: "#2563eb",
            color: "#ffffff",
            border: "2px solid #ffffff",
            boxShadow: "0 4px 14px rgba(37, 99, 235, 0.4)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "22px",
            transition: "transform 0.15s ease, background-color 0.15s ease",
          }}
          className="hover:scale-105 hover:bg-blue-700"
        >
          <span aria-hidden="true">♿</span>
        </button>
      </div>

      {/* Accessibility Dialog Modal / Drawer */}
      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="a11y-title"
          style={{
            position: "fixed",
            bottom: "80px",
            left: "24px",
            zIndex: 9985,
            width: "360px",
            maxWidth: "calc(100vw - 48px)",
            backgroundColor: "white",
            border: "1px solid #cbd5e1",
            borderRadius: "16px",
            boxShadow: "0 20px 40px rgba(15, 23, 42, 0.22)",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
            maxHeight: "80vh",
          }}
          ref={panelRef}
        >
          {/* Header */}
          <div
            style={{
              padding: "16px 20px",
              backgroundColor: "#f8fafc",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "18px" }}>♿</span>
              <h2 id="a11y-title" style={{ fontSize: "15px", fontWeight: 700, color: "#0f172a", margin: 0 }}>
                Accessibility &amp; Voice
              </h2>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close accessibility settings"
              style={{
                background: "none",
                border: "none",
                color: "#64748b",
                cursor: "pointer",
                fontSize: "18px",
                lineHeight: 1,
              }}
            >
              ✕
            </button>
          </div>

          {/* Body Settings */}
          <div style={{ padding: "18px 20px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "18px" }}>
            {/* 1. Text Size Scaling */}
            <div>
              <label style={{ display: "block", fontSize: "12.5px", fontWeight: 700, color: "#334155", marginBottom: "8px" }}>
                Text Size
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "6px" }}>
                {(
                  [
                    { id: "normal", label: "Standard", hint: "100%" },
                    { id: "large", label: "Large", hint: "115%" },
                    { id: "xlarge", label: "X-Large", hint: "130%" },
                  ] as { id: FontSizeOption; label: string; hint: string }[]
                ).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setFontSize(item.id)}
                    style={{
                      padding: "8px 6px",
                      borderRadius: "8px",
                      border: fontSize === item.id ? "2px solid #2563eb" : "1px solid #cbd5e1",
                      backgroundColor: fontSize === item.id ? "#eff6ff" : "#f8fafc",
                      color: fontSize === item.id ? "#1d4ed8" : "#475569",
                      fontWeight: 600,
                      fontSize: "12px",
                      cursor: "pointer",
                      textAlign: "center",
                    }}
                  >
                    <div>{item.label}</div>
                    <div style={{ fontSize: "10px", opacity: 0.75 }}>{item.hint}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* 2. High Contrast Theme */}
            <div>
              <label style={{ display: "block", fontSize: "12.5px", fontWeight: 700, color: "#334155", marginBottom: "8px" }}>
                Visual Contrast &amp; Theme
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "6px" }}>
                {(
                  [
                    { id: "standard", label: "Standard" },
                    { id: "high-contrast", label: "High Light" },
                    { id: "dark-contrast", label: "High Dark" },
                  ] as { id: ContrastOption; label: string }[]
                ).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setContrastMode(item.id)}
                    style={{
                      padding: "8px 6px",
                      borderRadius: "8px",
                      border: contrastMode === item.id ? "2px solid #2563eb" : "1px solid #cbd5e1",
                      backgroundColor: contrastMode === item.id ? "#eff6ff" : "#f8fafc",
                      color: contrastMode === item.id ? "#1d4ed8" : "#475569",
                      fontWeight: 600,
                      fontSize: "11.5px",
                      cursor: "pointer",
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 3. Toggles: Dyslexia Font & Reduced Motion */}
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <label style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", fontSize: "13px", color: "#1e293b" }}>
                <span style={{ fontWeight: 600 }}>Dyslexia-Friendly Font</span>
                <input
                  type="checkbox"
                  checked={dyslexicFont}
                  onChange={(e) => setDyslexicFont(e.target.checked)}
                  style={{ width: "16px", height: "16px", cursor: "pointer" }}
                />
              </label>

              <label style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", fontSize: "13px", color: "#1e293b" }}>
                <span style={{ fontWeight: 600 }}>Reduce Animations</span>
                <input
                  type="checkbox"
                  checked={reducedMotion}
                  onChange={(e) => setReducedMotion(e.target.checked)}
                  style={{ width: "16px", height: "16px", cursor: "pointer" }}
                />
              </label>
            </div>

            {/* 4. Vernacular Audio & Speech Settings */}
            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <label style={{ fontSize: "12.5px", fontWeight: 700, color: "#334155" }}>
                  🔊 Vernacular Voice Language
                </label>
                {isSpeaking && (
                  <span style={{ fontSize: "11px", color: "#059669", fontWeight: 700 }}>
                    Speaking...
                  </span>
                )}
              </div>

              <select
                value={speechLang}
                onChange={(e) => setSpeechLang(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px 10px",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13px",
                  backgroundColor: "#f8fafc",
                  color: "#1e293b",
                  outline: "none",
                  cursor: "pointer",
                }}
              >
                <option value="en-US">English (US / UK)</option>
                <option value="hi-IN">Hindi (हिंदी)</option>
                <option value="te-IN">Telugu (తెలుగు)</option>
                <option value="ta-IN">Tamil (தமிழ்)</option>
                <option value="es-ES">Spanish (Español)</option>
              </select>

              {/* Voice status info */}
              <div style={{ marginTop: "6px", fontSize: "11px", color: isNative ? "#166534" : "#475569" }}>
                {isNative
                  ? `🟢 Native voice active: ${activeVoiceName || "Detected"}`
                  : "⚡ Universal audio mode (Audible on this PC)"}
              </div>

              {/* Speed & Test button */}
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "10px" }}>
                <div style={{ flex: 1, display: "flex", gap: "4px" }}>
                  {[0.8, 1.0, 1.2].map((rate) => (
                    <button
                      key={rate}
                      type="button"
                      onClick={() => setSpeechRate(rate)}
                      style={{
                        flex: 1,
                        padding: "4px",
                        fontSize: "11px",
                        fontWeight: 600,
                        borderRadius: "6px",
                        border: speechRate === rate ? "1.5px solid #2563eb" : "1px solid #cbd5e1",
                        backgroundColor: speechRate === rate ? "#eff6ff" : "white",
                        color: speechRate === rate ? "#1d4ed8" : "#64748b",
                        cursor: "pointer",
                      }}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={isSpeaking ? stopSpeaking : testVoiceSample}
                  style={{
                    padding: "6px 12px",
                    borderRadius: "8px",
                    backgroundColor: isSpeaking ? "#dc2626" : "#2563eb",
                    color: "white",
                    fontWeight: 600,
                    fontSize: "12px",
                    border: "none",
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                  }}
                >
                  {isSpeaking ? "Stop" : "Test Voice"}
                </button>
              </div>
            </div>
          </div>

          {/* Footer: Reset defaults */}
          <div
            style={{
              padding: "12px 20px",
              backgroundColor: "#f8fafc",
              borderTop: "1px solid #e2e8f0",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <button
              type="button"
              onClick={resetDefaults}
              style={{
                background: "none",
                border: "none",
                color: "#64748b",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                padding: 0,
              }}
            >
              Reset Defaults
            </button>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>
              Shortcuts: Alt + A
            </span>
          </div>
        </div>
      )}
    </>
  );
}
