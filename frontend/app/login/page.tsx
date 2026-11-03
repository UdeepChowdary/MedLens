"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/Logo";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { signInWithGoogle, signInWithEmail, signUpWithEmail, isFirebaseReady } = useAuth();

  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsLoading(true);

    try {
      if (isSignUp) {
        await signUpWithEmail(email, password);
      } else {
        await signInWithEmail(email, password);
      }
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed";
      // Clean up common Firebase error codes into human-readable messages
      if (msg.includes("auth/user-not-found") || msg.includes("auth/wrong-password") || msg.includes("auth/invalid-credential")) {
        setErrorMsg("Invalid email or password. Please check your credentials.");
      } else if (msg.includes("auth/email-already-in-use")) {
        setErrorMsg("An account with this email already exists. Try signing in.");
      } else if (msg.includes("auth/weak-password")) {
        setErrorMsg("Password should be at least 6 characters.");
      } else {
        setErrorMsg(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setErrorMsg(null);
    setGoogleLoading(true);
    try {
      await signInWithGoogle();
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Google authentication failed";
      if (!msg.includes("popup-closed-by-user")) {
        setErrorMsg(msg);
      }
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "var(--surface)" }}>
      {/* Header */}
      <header style={{ padding: "24px 32px", borderBottom: "1px solid var(--border)", backgroundColor: "white" }}>
        <Logo />
      </header>

      {/* Login Card */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "24px" }}>
        <div
          style={{
            width: "100%",
            maxWidth: "420px",
            backgroundColor: "white",
            padding: "40px",
            borderRadius: "16px",
            boxShadow: "var(--shadow-md)",
            border: "1px solid var(--border)",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "28px" }}>
            <h1 style={{ fontSize: "26px", fontWeight: "bold", marginBottom: "6px", color: "var(--text-primary)" }}>
              {isSignUp ? "Create MedLens Account" : "Welcome Back"}
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>
              {isSignUp
                ? "Start verifying pharmaceutical packaging & clinical salts."
                : "Sign in to access your medicine scans & clinical reports."}
            </p>
            {!isFirebaseReady && (
              <div
                style={{
                  display: "inline-block",
                  marginTop: "10px",
                  padding: "4px 10px",
                  backgroundColor: "#eff6ff",
                  borderRadius: "9999px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "#2563eb",
                  border: "1px solid #bfdbfe",
                }}
              >
                ⚡ Offline / Demo Mode Active
              </div>
            )}
          </div>

          {errorMsg && (
            <div
              style={{
                marginBottom: "20px",
                padding: "12px 16px",
                borderRadius: "8px",
                backgroundColor: "#fef2f2",
                border: "1px solid #fecaca",
                color: "#dc2626",
                fontSize: "13px",
                lineHeight: "1.4",
              }}
            >
              {errorMsg}
            </div>
          )}

          {/* 1-Click Google Sign In */}
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={googleLoading || isLoading}
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "12px",
              padding: "12px 16px",
              borderRadius: "8px",
              border: "1px solid var(--border)",
              backgroundColor: "white",
              color: "var(--text-primary)",
              fontWeight: 500,
              fontSize: "14px",
              cursor: googleLoading ? "wait" : "pointer",
              transition: "all 0.15s ease",
            }}
            className="hover:bg-gray-50 focus:outline-none"
          >
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            {googleLoading ? "Signing In with Google..." : "Continue with Google"}
          </button>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              margin: "24px 0",
              color: "var(--text-secondary)",
              fontSize: "12px",
            }}
          >
            <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border)" }} />
            <span style={{ padding: "0 12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              or continue with email
            </span>
            <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border)" }} />
          </div>

          {/* Email / Password Form */}
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  fontWeight: 500,
                  marginBottom: "6px",
                  color: "var(--text-primary)",
                }}
              >
                Email Address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "1px solid var(--border)",
                  fontSize: "14px",
                  outline: "none",
                }}
                className="focus:border-[var(--blue)] focus:ring-1 focus:ring-[var(--blue)]"
              />
            </div>

            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  fontWeight: 500,
                  marginBottom: "6px",
                  color: "var(--text-primary)",
                }}
              >
                Password
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "1px solid var(--border)",
                  fontSize: "14px",
                  outline: "none",
                }}
                className="focus:border-[var(--blue)] focus:ring-1 focus:ring-[var(--blue)]"
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{
                width: "100%",
                marginTop: "8px",
                opacity: isLoading ? 0.7 : 1,
                padding: "12px",
                fontWeight: 600,
              }}
              disabled={isLoading || googleLoading}
            >
              {isLoading ? "Processing..." : isSignUp ? "Create Free Account" : "Sign In to Dashboard"}
            </button>
          </form>

          {/* Switch Sign Up / Sign In */}
          <div style={{ marginTop: "24px", textAlign: "center", fontSize: "14px", color: "var(--text-secondary)" }}>
            {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setErrorMsg(null);
              }}
              style={{
                background: "none",
                border: "none",
                color: "var(--blue)",
                fontWeight: 600,
                cursor: "pointer",
                padding: 0,
              }}
            >
              {isSignUp ? "Sign In" : "Sign Up"}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
