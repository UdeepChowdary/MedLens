"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/Logo";

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Mock authentication delay
    setTimeout(() => {
      router.push("/dashboard");
    }, 800);
  };

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "var(--surface)" }}>
      {/* Simple Header */}
      <header style={{ padding: "24px 32px", borderBottom: "1px solid var(--border)", backgroundColor: "white" }}>
        <Link href="/" style={{ textDecoration: "none" }}>
          <Logo />
        </Link>
      </header>

      {/* Login Form Container */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "24px" }}>
        <div style={{ 
          width: "100%", 
          maxWidth: "400px", 
          backgroundColor: "white", 
          padding: "40px", 
          borderRadius: "16px", 
          boxShadow: "var(--shadow-md)",
          border: "1px solid var(--border)"
        }}>
          <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "8px", textAlign: "center" }}>
            Welcome Back
          </h1>
          <p style={{ color: "var(--text-secondary)", textAlign: "center", marginBottom: "32px" }}>
            Sign in to access your MedLens dashboard.
          </p>

          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div>
              <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
                Email Address
              </label>
              <input 
                type="email" 
                placeholder="you@example.com" 
                required
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  border: "1px solid var(--border)",
                  fontSize: "15px",
                  outline: "none"
                }}
                className="focus:border-[var(--blue)] focus:ring-1 focus:ring-[var(--blue)]"
              />
            </div>
            
            <div>
              <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
                Password
              </label>
              <input 
                type="password" 
                placeholder="••••••••" 
                required
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  border: "1px solid var(--border)",
                  fontSize: "15px",
                  outline: "none"
                }}
                className="focus:border-[var(--blue)] focus:ring-1 focus:ring-[var(--blue)]"
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary"
              style={{ width: "100%", marginTop: "8px", opacity: isLoading ? 0.7 : 1 }}
              disabled={isLoading}
            >
              {isLoading ? "Signing In..." : "Sign In"}
            </button>
          </form>

          <div style={{ marginTop: "24px", textAlign: "center", fontSize: "14px", color: "var(--text-secondary)" }}>
            {"Don't have an account?"} <a href="#" style={{ color: "var(--blue)", fontWeight: 500, textDecoration: "none" }}>Sign up</a>
          </div>
        </div>
      </div>
    </main>
  );
}
