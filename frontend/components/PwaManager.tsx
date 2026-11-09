"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
}

export default function PwaManager() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isStandalone, setIsStandalone] = useState(false);
  const [isIos, setIsIos] = useState(false);
  const [showIosGuide, setShowIosGuide] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [showOnlineToast, setShowOnlineToast] = useState(false);

  useEffect(() => {
    // 1. Register Service Worker
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      navigator.serviceWorker
        .register("/sw.js")
        .then((reg) => {
          console.log("[MedLens PWA] Service Worker registered with scope:", reg.scope);
        })
        .catch((err) => {
          console.warn("[MedLens PWA] Service Worker registration failed:", err);
        });
    }

    // 2. Check if already running standalone
    const checkStandalone = () => {
      const isStandaloneMode =
        window.matchMedia("(display-mode: standalone)").matches ||
        (window.navigator as unknown as { standalone?: boolean }).standalone === true;
      setIsStandalone(isStandaloneMode);
    };
    checkStandalone();

    // 3. Detect iOS device
    const userAgent = window.navigator.userAgent.toLowerCase();
    const isIosDevice = /iphone|ipad|ipod/.test(userAgent) && !(window as unknown as { MSStream?: unknown }).MSStream;
    setIsIos(isIosDevice);

    // 4. Check dismissal preference in localStorage
    const dismissedTime = localStorage.getItem("medlens_pwa_dismissed");
    if (dismissedTime) {
      const pastTime = parseInt(dismissedTime, 10);
      // Suppress for 2 days after dismissal
      if (Date.now() - pastTime < 2 * 24 * 60 * 60 * 1000) {
        setIsDismissed(true);
      }
    }

    // 5. Intercept beforeinstallprompt for Android & Chromium
    const handleBeforeInstall = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstall);

    // 6. Network connectivity listeners
    const handleOnline = () => {
      setIsOffline(false);
      setShowOnlineToast(true);
      setTimeout(() => setShowOnlineToast(false), 3500);
    };
    const handleOffline = () => {
      setIsOffline(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    if (!navigator.onLine) {
      setIsOffline(true);
    }

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstall);
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleInstallClick = async () => {
    if (isIos) {
      setShowIosGuide(!showIosGuide);
      return;
    }

    if (!deferredPrompt) {
      // Fallback instruction
      alert("To install MedLens: Open your browser menu (⋮) and tap 'Install App' or 'Add to Home Screen'.");
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setDeferredPrompt(null);
      setIsDismissed(true);
    }
  };

  const handleDismiss = () => {
    setIsDismissed(true);
    localStorage.setItem("medlens_pwa_dismissed", Date.now().toString());
  };

  // Do not render install prompt if already installed (standalone) or dismissed
  const canShowPrompt = !isStandalone && !isDismissed && (deferredPrompt !== null || isIos);

  return (
    <>
      {/* Offline Toast Notification */}
      {isOffline && (
        <div
          role="status"
          style={{
            position: "fixed",
            top: "12px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 9999,
            backgroundColor: "#0f172a",
            color: "#f8fafc",
            border: "1px solid #334155",
            padding: "8px 16px",
            borderRadius: "24px",
            fontSize: "13px",
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            boxShadow: "0 10px 25px rgba(0,0,0,0.2)",
            animation: "fadeIn 0.2s ease-out",
          }}
        >
          <span style={{ color: "#eab308" }}>⚡</span>
          <span>You are currently offline. MedLens is running in cached local mode.</span>
        </div>
      )}

      {/* Online Restored Toast Notification */}
      {showOnlineToast && (
        <div
          role="status"
          style={{
            position: "fixed",
            top: "12px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 9999,
            backgroundColor: "#059669",
            color: "#ffffff",
            padding: "8px 16px",
            borderRadius: "24px",
            fontSize: "13px",
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
          }}
        >
          <span>✓</span>
          <span>Connection restored. Live clinical sync active.</span>
        </div>
      )}

      {/* Floating PWA Install Banner */}
      {canShowPrompt && (
        <aside
          aria-label="Install MedLens application"
          style={{
            position: "fixed",
            bottom: "20px",
            right: "20px",
            zIndex: 9990,
            maxWidth: "380px",
            width: "calc(100% - 40px)",
            backgroundColor: "#ffffff",
            border: "1px solid #cbd5e1",
            borderRadius: "16px",
            padding: "14px 16px",
            boxShadow: "0 12px 32px rgba(15,23,42,0.15)",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            animation: "slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
          }}
        >
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "10px",
                  backgroundColor: "#0f172a",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                  position: "relative",
                  boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                }}
              >
                <Image
                  src="/icons/icon-192x192.png"
                  alt="MedLens App Icon"
                  width={44}
                  height={44}
                  style={{ objectFit: "cover" }}
                />
              </div>

              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "#0f172a" }}>Install MedLens</span>
                  <span
                    style={{
                      fontSize: "10px",
                      fontWeight: 700,
                      backgroundColor: "#eff6ff",
                      color: "#2563eb",
                      padding: "1px 6px",
                      borderRadius: "8px",
                      border: "1px solid #bfdbfe",
                    }}
                  >
                    App
                  </span>
                </div>
                <p style={{ fontSize: "12px", color: "#64748b", margin: "2px 0 0 0", lineHeight: "1.3" }}>
                  Full-screen camera scanning, zero address bar, &amp; offline monograph access.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleDismiss}
              aria-label="Dismiss app installation prompt"
              style={{
                background: "none",
                border: "none",
                color: "#94a3b8",
                cursor: "pointer",
                padding: "2px",
                fontSize: "16px",
                lineHeight: "1",
              }}
            >
              ✕
            </button>
          </div>

          {/* Action buttons */}
          <div style={{ display: "flex", gap: "8px", marginTop: "2px" }}>
            <button
              type="button"
              onClick={handleInstallClick}
              style={{
                flex: 1,
                backgroundColor: "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "8px 14px",
                fontSize: "12.5px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "6px",
                boxShadow: "0 2px 6px rgba(37,99,235,0.25)",
              }}
            >
              <span>{isIos ? "How to Install (iOS)" : "Install App"}</span>
              <span>→</span>
            </button>

            <button
              type="button"
              onClick={handleDismiss}
              style={{
                backgroundColor: "#f8fafc",
                color: "#64748b",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                padding: "8px 12px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Later
            </button>
          </div>

          {/* iOS Safari Installation Steps Tooltip */}
          {showIosGuide && isIos && (
            <div
              style={{
                backgroundColor: "#f8fafc",
                border: "1px solid #cbd5e1",
                borderRadius: "10px",
                padding: "10px 12px",
                fontSize: "11.5px",
                color: "#334155",
                lineHeight: "1.5",
              }}
            >
              <div style={{ fontWeight: 700, color: "#0f172a", marginBottom: "4px" }}>
                Add to iPhone / iPad Home Screen:
              </div>
              <ol style={{ margin: 0, paddingLeft: "16px" }}>
                <li>
                  Tap the <strong>Share</strong> button (📤) in Safari&apos;s bottom toolbar.
                </li>
                <li>
                  Scroll down and tap <strong>&ldquo;Add to Home Screen&rdquo;</strong> (➕).
                </li>
                <li>
                  Tap <strong>Add</strong> in the top right to launch MedLens as a standalone app.
                </li>
              </ol>
            </div>
          )}
        </aside>
      )}

      <style jsx global>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translate(-50%, -10px);
          }
          to {
            opacity: 1;
            transform: translate(-50%, 0);
          }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  );
}
