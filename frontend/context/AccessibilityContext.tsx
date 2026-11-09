"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";

export type FontSizeOption = "normal" | "large" | "xlarge";
export type ContrastOption = "standard" | "high-contrast" | "dark-contrast";

export interface AccessibilitySettings {
  fontSize: FontSizeOption;
  contrastMode: ContrastOption;
  dyslexicFont: boolean;
  reducedMotion: boolean;
  speechLang: string;
  speechRate: number;
}

interface AccessibilityContextType extends AccessibilitySettings {
  setFontSize: (size: FontSizeOption) => void;
  setContrastMode: (mode: ContrastOption) => void;
  setDyslexicFont: (enabled: boolean) => void;
  setReducedMotion: (enabled: boolean) => void;
  setSpeechLang: (lang: string) => void;
  setSpeechRate: (rate: number) => void;
  speak: (text: string, onEnd?: () => void, customLang?: string) => void;
  stopSpeaking: () => void;
  isSpeaking: boolean;
  availableVoices: SpeechSynthesisVoice[];
  hasNativeVoice: (langCode: string) => boolean;
  getBestVoiceForLang: (langCode: string) => SpeechSynthesisVoice | undefined;
  activeVoiceName: string | null;
  resetDefaults: () => void;
}

const DEFAULT_SETTINGS: AccessibilitySettings = {
  fontSize: "normal",
  contrastMode: "standard",
  dyslexicFont: false,
  reducedMotion: false,
  speechLang: "en-US",
  speechRate: 1.0,
};

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const AccessibilityProvider = ({ children }: { children: React.ReactNode }) => {
  const [fontSize, setFontSizeState] = useState<FontSizeOption>("normal");
  const [contrastMode, setContrastModeState] = useState<ContrastOption>("standard");
  const [dyslexicFont, setDyslexicFontState] = useState<boolean>(false);
  const [reducedMotion, setReducedMotionState] = useState<boolean>(false);
  const [speechLang, setSpeechLangState] = useState<string>("en-US");
  const [speechRate, setSpeechRateState] = useState<number>(1.0);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [activeVoiceName, setActiveVoiceName] = useState<string | null>(null);

  const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 1. Populate system voices dynamically (handles async onvoiceschanged in Chromium/Edge/Safari)
  useEffect(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    const populateVoices = () => {
      try {
        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length > 0) {
          setAvailableVoices(voices);
        }
      } catch {
        // Voice loading fallback
      }
    };

    populateVoices();
    window.speechSynthesis.onvoiceschanged = populateVoices;

    // Retry once after 250ms for browsers that delay speech engine loading
    const timer = setTimeout(populateVoices, 250);

    return () => {
      clearTimeout(timer);
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  // 2. Load initial settings from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("medlens_a11y");
      if (saved) {
        const parsed = JSON.parse(saved) as Partial<AccessibilitySettings>;
        if (parsed.fontSize) setFontSizeState(parsed.fontSize);
        if (parsed.contrastMode) setContrastModeState(parsed.contrastMode);
        if (typeof parsed.dyslexicFont === "boolean") setDyslexicFontState(parsed.dyslexicFont);
        if (typeof parsed.reducedMotion === "boolean") setReducedMotionState(parsed.reducedMotion);
        if (parsed.speechLang) setSpeechLangState(parsed.speechLang);
        if (parsed.speechRate) setSpeechRateState(parsed.speechRate);
      } else {
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
          setReducedMotionState(true);
        }
      }
    } catch {
      // Storage fallback
    }
  }, []);

  // 3. Synchronize DOM classes whenever visual a11y preferences change
  useEffect(() => {
    if (typeof document === "undefined") return;
    const root = document.documentElement;

    root.classList.remove("a11y-font-large", "a11y-font-xlarge");
    if (fontSize === "large") root.classList.add("a11y-font-large");
    if (fontSize === "xlarge") root.classList.add("a11y-font-xlarge");

    root.classList.remove("a11y-contrast-high", "a11y-contrast-dark");
    if (contrastMode === "high-contrast") root.classList.add("a11y-contrast-high");
    if (contrastMode === "dark-contrast") root.classList.add("a11y-contrast-dark");

    if (dyslexicFont) {
      root.classList.add("a11y-dyslexic");
    } else {
      root.classList.remove("a11y-dyslexic");
    }

    if (reducedMotion) {
      root.classList.add("a11y-reduced-motion");
    } else {
      root.classList.remove("a11y-reduced-motion");
    }

    try {
      const toSave: AccessibilitySettings = {
        fontSize,
        contrastMode,
        dyslexicFont,
        reducedMotion,
        speechLang,
        speechRate,
      };
      localStorage.setItem("medlens_a11y", JSON.stringify(toSave));
    } catch {
      // Storage fallback
    }
  }, [fontSize, contrastMode, dyslexicFont, reducedMotion, speechLang, speechRate]);

  // Find best matching voice for a given language code
  const getBestVoiceForLang = useCallback(
    (langCode: string): SpeechSynthesisVoice | undefined => {
      const voices =
        availableVoices.length > 0
          ? availableVoices
          : typeof window !== "undefined" && "speechSynthesis" in window
          ? window.speechSynthesis.getVoices()
          : [];

      const prefix = langCode.split("-")[0].toLowerCase();
      const langNames: Record<string, string[]> = {
        hi: ["hindi", "हिन्दी", "swara", "madhur", "kalpana", "hemant"],
        te: ["telugu", "తెలుగు", "mohan", "shruti"],
        ta: ["tamil", "தமிழ்", "pallavi", "valluvar"],
        es: ["spanish", "español", "espanol", "helena", "laura", "pablo"],
        en: ["english", "david", "zira", "george", "susan", "hazel"],
      };
      const targets = langNames[prefix] || [prefix];

      // 1. Exact match e.g. hi-IN
      let match = voices.find((v) => v.lang.toLowerCase().replace("_", "-") === langCode.toLowerCase());
      if (match) return match;

      // 2. Prefix match e.g. hi
      match = voices.find((v) => v.lang.toLowerCase().replace("_", "-").startsWith(prefix));
      if (match) return match;

      // 3. Name match e.g. "Swara Online (Natural) - Hindi"
      match = voices.find((v) => {
        const vName = v.name.toLowerCase();
        return targets.some((t) => vName.includes(t));
      });
      return match;
    },
    [availableVoices]
  );

  // Check if current device has a native TTS voice installed for the given language
  const hasNativeVoice = useCallback(
    (langCode: string): boolean => {
      return getBestVoiceForLang(langCode) !== undefined;
    },
    [getBestVoiceForLang]
  );

  // Setters
  const setFontSize = (size: FontSizeOption) => setFontSizeState(size);
  const setContrastMode = (mode: ContrastOption) => setContrastModeState(mode);
  const setDyslexicFont = (enabled: boolean) => setDyslexicFontState(enabled);
  const setReducedMotion = (enabled: boolean) => setReducedMotionState(enabled);
  const setSpeechLang = (lang: string) => setSpeechLangState(lang);
  const setSpeechRate = (rate: number) => setSpeechRateState(rate);

  // Text-To-Speech (Web Speech API) with cross-browser engine and fallback handling
  const speak = useCallback(
    (text: string, onEnd?: () => void, customLang?: string) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window)) {
        alert("Text-to-speech is not supported by your browser.");
        return;
      }

      // Clear any prior keepalive
      if (keepAliveRef.current) {
        clearInterval(keepAliveRef.current);
        keepAliveRef.current = null;
      }

      // Cancel any ongoing speech and ensure synthesis is unpaused
      window.speechSynthesis.cancel();
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }

      const targetLang = customLang || speechLang;

      // Clean up markdown / symbols
      const cleanText = text
        .replace(/[*#_~`]/g, " ")
        .replace(/\[.*?\]/g, " ")
        .replace(/\s+/g, " ")
        .trim();

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = speechRate;

      const matchedVoice = getBestVoiceForLang(targetLang);
      const voices =
        availableVoices.length > 0
          ? availableVoices
          : window.speechSynthesis.getVoices();

      if (matchedVoice) {
        utterance.voice = matchedVoice;
        utterance.lang = matchedVoice.lang;
        setActiveVoiceName(matchedVoice.name);
      } else {
        // Fallback: Use default system voice (usually English) to speak Romanized phonetic text
        utterance.lang = "en-US";
        const defaultVoice =
          voices.find((v) => v.default) ||
          voices.find((v) => v.lang.toLowerCase().startsWith("en")) ||
          voices[0];

        if (defaultVoice) {
          utterance.voice = defaultVoice;
          setActiveVoiceName(`${defaultVoice.name} (Phonetic Voice)`);
        } else {
          setActiveVoiceName("System Default");
        }
      }

      utterance.onstart = () => {
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        if (keepAliveRef.current) {
          clearInterval(keepAliveRef.current);
          keepAliveRef.current = null;
        }
        setIsSpeaking(false);
        setActiveVoiceName(null);
        if (onEnd) onEnd();
      };

      utterance.onerror = (e) => {
        if (keepAliveRef.current) {
          clearInterval(keepAliveRef.current);
          keepAliveRef.current = null;
        }
        console.warn("[MedLens TTS] Speech error:", e);
        setIsSpeaking(false);
        setActiveVoiceName(null);
      };

      // Chromium keep-alive interval: Prevents browser garbage collection pausing long utterances (>15s)
      keepAliveRef.current = setInterval(() => {
        if (typeof window !== "undefined" && "speechSynthesis" in window && window.speechSynthesis.speaking) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }
      }, 9000);

      // 40ms timeout ensures Chrome completes previous audio buffer teardown
      setTimeout(() => {
        window.speechSynthesis.speak(utterance);
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
      }, 40);
    },
    [speechLang, speechRate, availableVoices, getBestVoiceForLang]
  );

  const stopSpeaking = useCallback(() => {
    if (keepAliveRef.current) {
      clearInterval(keepAliveRef.current);
      keepAliveRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setActiveVoiceName(null);
    }
  }, []);

  const resetDefaults = () => {
    setFontSizeState(DEFAULT_SETTINGS.fontSize);
    setContrastModeState(DEFAULT_SETTINGS.contrastMode);
    setDyslexicFontState(DEFAULT_SETTINGS.dyslexicFont);
    setReducedMotionState(DEFAULT_SETTINGS.reducedMotion);
    setSpeechLangState(DEFAULT_SETTINGS.speechLang);
    setSpeechRateState(DEFAULT_SETTINGS.speechRate);
    stopSpeaking();
  };

  return (
    <AccessibilityContext.Provider
      value={{
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
        availableVoices,
        hasNativeVoice,
        getBestVoiceForLang,
        activeVoiceName,
        resetDefaults,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = (): AccessibilityContextType => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error("useAccessibility must be used within an AccessibilityProvider");
  }
  return context;
};
