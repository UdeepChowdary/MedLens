"use client";

import React, { useState } from "react";
import { useAccessibility } from "@/context/AccessibilityContext";
import { AnalysisResponse } from "@/lib/api";

interface VoiceReadoutProps {
  report: AnalysisResponse;
}

type ScriptMode = "auto" | "native" | "phonetic";

export default function VoiceReadout({ report }: VoiceReadoutProps) {
  const {
    speak,
    stopSpeaking,
    isSpeaking,
    speechLang,
    setSpeechLang,
    hasNativeVoice,
    activeVoiceName,
  } = useAccessibility();

  const [scriptMode, setScriptMode] = useState<ScriptMode>("auto");
  const [showTranscript, setShowTranscript] = useState(false);

  const medName = report.product.detected_name || "Prescribed Medicine";
  const actives =
    report.active_ingredients
      .map((ing) => `${ing.canonical_name} ${ing.strength?.raw_text || ""}`.trim())
      .join(", ") || "Active salts";

  const purposeRaw = (report.safety_profile?.purpose_summary || "").toLowerCase();
  const precautionsRaw = (report.safety_profile?.precautions || []).join(". ").toLowerCase();

  // Detect clinical category for vernacular phrases
  const getClinicalCategory = () => {
    const combined = `${medName} ${actives} ${purposeRaw} ${precautionsRaw}`.toLowerCase();
    if (
      combined.includes("paracetamol") ||
      combined.includes("fever") ||
      combined.includes("analgesic") ||
      combined.includes("pain") ||
      combined.includes("aceclofenac") ||
      combined.includes("ibuprofen") ||
      combined.includes("diclofenac")
    ) {
      return "fever_pain";
    }
    if (
      combined.includes("telmisartan") ||
      combined.includes("amlodipine") ||
      combined.includes("pressure") ||
      combined.includes("hypertension")
    ) {
      return "bp";
    }
    if (
      combined.includes("metformin") ||
      combined.includes("glimepiride") ||
      combined.includes("diabetes") ||
      combined.includes("insulin") ||
      combined.includes("sugar")
    ) {
      return "diabetes";
    }
    if (
      combined.includes("pantoprazole") ||
      combined.includes("omeprazole") ||
      combined.includes("acid") ||
      combined.includes("reflux") ||
      combined.includes("gastric")
    ) {
      return "acidity";
    }
    if (
      combined.includes("amoxicillin") ||
      combined.includes("azithromycin") ||
      combined.includes("antibiotic") ||
      combined.includes("infection")
    ) {
      return "infection";
    }
    if (
      combined.includes("cetirizine") ||
      combined.includes("cough") ||
      combined.includes("cold") ||
      combined.includes("allergy")
    ) {
      return "cold_allergy";
    }
    return "general";
  };

  const category = getClinicalCategory();

  // Determine whether to use native script or phonetic Romanized
  const isNativeSupported = hasNativeVoice(speechLang);
  const effectiveMode: "native" | "phonetic" =
    scriptMode === "auto"
      ? isNativeSupported
        ? "native"
        : "phonetic"
      : scriptMode;

  const generateSummary = (lang: string, mode: "native" | "phonetic") => {
    // 1. HINDI
    if (lang.startsWith("hi")) {
      if (mode === "native") {
        const purposes: Record<string, string> = {
          fever_pain: "बुखार कम करने और शरीर के दर्द में राहत पाने",
          bp: "हाई ब्लड प्रेशर (उच्च रक्तचाप) को नियंत्रित रखने",
          diabetes: "ब्लड शुगर (मधुमेह) के स्तर को संतुलित रखने",
          acidity: "पेट में एसिडिटी, जलन और गैस को कम करने",
          infection: "बैक्टीरियल इन्फेक्शन (संक्रमण) को ठीक करने",
          cold_allergy: "खांसी, जुकाम और एलर्जी के लक्षणों को शांत करने",
          general: "चिकित्सीय उपचार और स्वास्थ्य लाभ",
        };
        const p = purposes[category] || purposes.general;
        return `यह दवा ${medName} है। इसमें मुख्य सक्रिय रासायनिक घटक हैं: ${actives}। इसका उपयोग ${p} के लिए किया जाता है। महत्वपूर्ण सूचना: दवा की खुराक डॉक्टर के पर्चे के अनुसार ही लें। बिना चिकित्सीय परामर्श खुराक में बदलाव न करें।`;
      } else {
        // Phonetic Romanized Hindi (Clean pronunciation for English voices)
        const purposesPhonetic: Record<string, string> = {
          fever_pain: "bukhaar aur jism ke dard ko kam karne",
          bp: "high blood pressure ko control mein rakhne",
          diabetes: "blood sugar ko santulit rakhne",
          acidity: "pet mein acidity aur jalan kam karne",
          infection: "bacterial infection theek karne",
          cold_allergy: "khaansi, zukham aur allergy theek karne",
          general: "bimari ka ilaj karne",
        };
        const p = purposesPhonetic[category] || purposesPhonetic.general;
        return `Yeh dawai ${medName} hai. Is dawai mein mukhya active medicine ${actives} hai. Iska istemal ${p} ke liye hota hai. Kripya dhyan dein: yeh dawai doctor ke bataye anusaar lein. Apne aap dose na badlein.`;
      }
    }

    // 2. TELUGU
    if (lang.startsWith("te")) {
      if (mode === "native") {
        const purposesTe: Record<string, string> = {
          fever_pain: "జ్వరం మరియు ఒంటి నొప్పులు తగ్గించడానికి",
          bp: "రక్తపోటు (బ్లడ్ ప్రెజర్) నియంత్రణలో ఉంచడానికి",
          diabetes: "షుగర్ (మధుమేహం) స్థాయిలను అదుపులో ఉంచడానికి",
          acidity: "కడుపులో మంట, ఎసిడిటీ తగ్గించడానికి",
          infection: "ఇన్ఫెక్షన్ తగ్గించడానికి",
          cold_allergy: "దగ్గు, జలుబు మరియు అలర్జీ తగ్గించడానికి",
          general: "వైద్య చికిత్స మరియు ఆరోగ్య రక్షణ కొరకు",
        };
        const p = purposesTe[category] || purposesTe.general;
        return `ఈ మందు పేరు ${medName}। ఇందులో ప్రధాన ఔషధ పదార్థాలు: ${actives}। దీని ఉపయోగం: ${p}। ముఖ్యమైన సూచన: వైద్యుల సలహా మేరకే ఈ మందు వాడాలి.`;
      } else {
        // Phonetic Romanized Telugu
        const purposesTePhonetic: Record<string, string> = {
          fever_pain: "jvaram mariyu body pains thagginchataniki",
          bp: "high blood pressure control cheyataniki",
          diabetes: "blood sugar level control cheyataniki",
          acidity: "kadupulo manta mariyu acidity thagginchataniki",
          infection: "bacterial infection theek cheyataniki",
          cold_allergy: "daggu mariyu jalubu thagginchataniki",
          general: "doctor prescribe chesina ilaj koraku",
        };
        const p = purposesTePhonetic[category] || purposesTePhonetic.general;
        return `Ee mandhu peru ${medName}. Ee mandhulo active ingredients ${actives} unnaayi. Deeni upayogam: ${p}. Mukhyamaina jaagratha: Doctor salahatho maathrame ee mandhu vaadandi.`;
      }
    }

    // 3. TAMIL
    if (lang.startsWith("ta")) {
      if (mode === "native") {
        const purposesTa: Record<string, string> = {
          fever_pain: "காய்ச்சல் மற்றும் உடல் வலியை குறைக்க",
          bp: "இரத்த அழுத்தத்தை சீராக வைத்திருக்க",
          diabetes: "சர்க்கரை அளவை கட்டுப்பாட்டில் வைக்க",
          acidity: "நெஞ்செரிச்சல் மற்றும் அசிடிட்டியை தணிக்க",
          infection: "தொற்று நோய்களை குணப்படுத்த",
          cold_allergy: "இருமல், சளி மற்றும் ஒவ்வாமையை போக்க",
          general: "மருத்துவ சிகிச்சைக்காக",
        };
        const p = purposesTa[category] || purposesTa.general;
        return `இந்த மருந்து ${medName} ஆகும். இதில் உள்ள முக்கிய மூலப்பொருட்கள்: ${actives}. இதன் பயன்பாடு: ${p}. மருத்துவரின் ஆலோசனைப்படி மட்டுமே உட்கொள்ள வேண்டும்.`;
      } else {
        // Phonetic Romanized Tamil
        const purposesTaPhonetic: Record<string, string> = {
          fever_pain: "kaichal matrum udal valiyai kuraikka",
          bp: "blood pressure kattu padutha",
          diabetes: "sugar alavai control seiya",
          acidity: "nenjerichal matrum acidity thagga",
          infection: "infection gunamaakka",
          cold_allergy: "irumal matrum sali kuraikka",
          general: "maruthuva sigichaikkaga",
        };
        const p = purposesTaPhonetic[category] || purposesTaPhonetic.general;
        return `Indha marundhu ${medName}. Idhil ulla active ingredients ${actives}. Idhan payanpaadu: ${p}. Kurippu: Ungal doctor sonnapadi mattume indha marundhai saappidavum.`;
      }
    }

    // 4. SPANISH
    if (lang.startsWith("es")) {
      const purposesEs: Record<string, string> = {
        fever_pain: "aliviar la fiebre y los dolores corporales",
        bp: "controlar la hipertensión arterial",
        diabetes: "regular los niveles de glucosa en sangre",
        acidity: "reducir la acidez y el reflujo gástrico",
        infection: "tratar infecciones bacterianas",
        cold_allergy: "aliviar los síntomas de congestión y alergia",
        general: "el tratamiento médico recetado",
      };
      const p = purposesEs[category] || purposesEs.general;
      return `Este medicamento es ${medName}. Contiene los ingredientes activos: ${actives}. Su indicación principal es: ${p}. Tome siempre la dosis exacta recetada por su médico.`;
    }

    // 5. ENGLISH (DEFAULT)
    const purposeEn =
      report.safety_profile?.purpose_summary || "prescribed therapeutic treatment";
    const precautionsEn =
      report.safety_profile?.precautions?.slice(0, 2).join(". ") ||
      "Take strictly as advised by your physician";
    return `Verified Medicine: ${medName}. Active pharmaceutical ingredients: ${actives}. Purpose: ${purposeEn}. Key clinical instructions: ${precautionsEn}. Always consult your doctor before modifying medication.`;
  };

  const currentSummaryText = generateSummary(speechLang, effectiveMode);

  const handlePlayVoice = (langToPlay?: string) => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      const targetLang = langToPlay || speechLang;
      const targetMode: "native" | "phonetic" =
        scriptMode === "auto"
          ? hasNativeVoice(targetLang)
            ? "native"
            : "phonetic"
          : scriptMode;

      const summaryText = generateSummary(targetLang, targetMode);
      speak(summaryText, undefined, targetLang);
    }
  };

  const handleLanguageSelect = (newLang: string) => {
    const wasSpeaking = isSpeaking;
    if (wasSpeaking) stopSpeaking();
    setSpeechLang(newLang);

    if (wasSpeaking) {
      setTimeout(() => {
        handlePlayVoice(newLang);
      }, 120);
    }
  };

  const languages = [
    { code: "en-US", label: "English" },
    { code: "hi-IN", label: "हिंदी" },
    { code: "te-IN", label: "తెలుగు" },
    { code: "ta-IN", label: "தமிழ்" },
    { code: "es-ES", label: "Español" },
  ];

  return (
    <div
      style={{
        backgroundColor: "#ffffff",
        border: "1px solid #cbd5e1",
        borderRadius: "16px",
        padding: "18px 22px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
        display: "flex",
        flexDirection: "column",
        gap: "14px",
      }}
    >
      {/* Top Row: Play Button, Status Title & Badges */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <button
            type="button"
            onClick={() => handlePlayVoice()}
            aria-label={
              isSpeaking ? "Stop voice readout" : "Listen to audio summary of this medicine"
            }
            style={{
              width: "46px",
              height: "46px",
              borderRadius: "50%",
              backgroundColor: isSpeaking ? "#dc2626" : "#2563eb",
              color: "white",
              border: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "20px",
              cursor: "pointer",
              flexShrink: 0,
              transition: "all 0.15s ease",
              boxShadow: isSpeaking
                ? "0 0 16px rgba(220, 38, 38, 0.45)"
                : "0 4px 12px rgba(37, 99, 235, 0.3)",
            }}
            className="hover:scale-105"
          >
            {isSpeaking ? "⏹" : "🔊"}
          </button>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
              <span style={{ fontSize: "15px", fontWeight: 700, color: "#0f172a" }}>
                {isSpeaking
                  ? "Speaking Medicine Instructions..."
                  : "Listen to Spoken Instructions"}
              </span>
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  backgroundColor: isSpeaking ? "#fee2e2" : "#eff6ff",
                  color: isSpeaking ? "#dc2626" : "#2563eb",
                  padding: "2px 8px",
                  borderRadius: "12px",
                  border: `1px solid ${isSpeaking ? "#fecaca" : "#bfdbfe"}`,
                }}
              >
                {isSpeaking ? "Live Audio Active" : "Vernacular Audio AI"}
              </span>
            </div>
            <p style={{ fontSize: "12.5px", color: "#64748b", margin: "2px 0 0 0" }}>
              High-clarity medical audio for elderly patients &amp; vernacular speakers.
            </p>
          </div>
        </div>

        {/* Script Mode & Voice Status Info */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          <span
            style={{
              fontSize: "11px",
              fontWeight: 600,
              padding: "3px 8px",
              borderRadius: "8px",
              backgroundColor: isNativeSupported ? "#f0fdf4" : "#f8fafc",
              color: isNativeSupported ? "#166534" : "#475569",
              border: `1px solid ${isNativeSupported ? "#bbf7d0" : "#e2e8f0"}`,
            }}
          >
            {isNativeSupported
              ? `🟢 Native Voice: ${activeVoiceName || "Detected"}`
              : "⚡ Universal Audio Engine (Audible on all PCs)"}
          </span>

          <button
            type="button"
            onClick={() => setShowTranscript((prev) => !prev)}
            style={{
              fontSize: "11.5px",
              fontWeight: 600,
              padding: "3px 10px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              backgroundColor: showTranscript ? "#f1f5f9" : "#ffffff",
              color: "#334155",
              cursor: "pointer",
            }}
          >
            {showTranscript ? "Hide Text" : "View Spoken Text"}
          </button>
        </div>
      </div>

      {/* Middle Controls: Language Selector Pills and Script Switcher */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "10px",
          borderTop: "1px solid #f1f5f9",
          paddingTop: "12px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
          <span
            style={{ fontSize: "12px", fontWeight: 600, color: "#475569", marginRight: "2px" }}
          >
            Language:
          </span>
          {languages.map((l) => {
            const isSelected = speechLang === l.code;
            return (
              <button
                key={l.code}
                type="button"
                onClick={() => handleLanguageSelect(l.code)}
                style={{
                  fontSize: "12px",
                  fontWeight: 600,
                  padding: "4px 12px",
                  borderRadius: "16px",
                  border: isSelected ? "1.5px solid #2563eb" : "1px solid #cbd5e1",
                  backgroundColor: isSelected ? "#eff6ff" : "#f8fafc",
                  color: isSelected ? "#1d4ed8" : "#475569",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                {l.label}
              </button>
            );
          })}
        </div>

        {/* Script Mode Switcher (Native Script vs Romanized Phonetic) */}
        {!speechLang.startsWith("en") && (
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 600 }}>Script:</span>
            <button
              type="button"
              onClick={() => {
                setScriptMode("phonetic");
                if (isSpeaking) {
                  stopSpeaking();
                  setTimeout(() => {
                    const txt = generateSummary(speechLang, "phonetic");
                    speak(txt, undefined, speechLang);
                  }, 120);
                }
              }}
              style={{
                fontSize: "11px",
                fontWeight: 600,
                padding: "2px 8px",
                borderRadius: "6px",
                border:
                  effectiveMode === "phonetic" ? "1.5px solid #2563eb" : "1px solid #cbd5e1",
                backgroundColor: effectiveMode === "phonetic" ? "#eff6ff" : "white",
                color: effectiveMode === "phonetic" ? "#1d4ed8" : "#64748b",
                cursor: "pointer",
              }}
              title="Uses Romanized characters for clear audio on systems without regional voice packs"
            >
              Phonetic (Hinglish)
            </button>
            <button
              type="button"
              onClick={() => {
                setScriptMode("native");
                if (isSpeaking) {
                  stopSpeaking();
                  setTimeout(() => {
                    const txt = generateSummary(speechLang, "native");
                    speak(txt, undefined, speechLang);
                  }, 120);
                }
              }}
              style={{
                fontSize: "11px",
                fontWeight: 600,
                padding: "2px 8px",
                borderRadius: "6px",
                border: effectiveMode === "native" ? "1.5px solid #2563eb" : "1px solid #cbd5e1",
                backgroundColor: effectiveMode === "native" ? "#eff6ff" : "white",
                color: effectiveMode === "native" ? "#1d4ed8" : "#64748b",
                cursor: "pointer",
              }}
              title="Uses original Devanagari / Telugu / Tamil script"
            >
              Native Script
            </button>
          </div>
        )}
      </div>

      {/* Expandable Spoken Transcript Preview */}
      {showTranscript && (
        <div
          style={{
            backgroundColor: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: "10px",
            padding: "12px 14px",
            fontSize: "13px",
            color: "#1e293b",
            lineHeight: "1.6",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "6px",
            }}
          >
            <span
              style={{
                fontSize: "11px",
                fontWeight: 700,
                color: "#475569",
                textTransform: "uppercase",
              }}
            >
              Spoken Transcript ({effectiveMode === "native" ? "Native Script" : "Phonetic Romanized"})
            </span>
            <button
              type="button"
              onClick={() => {
                navigator.clipboard.writeText(currentSummaryText);
              }}
              style={{
                fontSize: "11px",
                color: "#2563eb",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              📋 Copy
            </button>
          </div>
          <p style={{ margin: 0 }}>{currentSummaryText}</p>
        </div>
      )}
    </div>
  );
}
