"use client";

import React, { useState, useEffect } from "react";

/* ============================================================
   SVG ICONS (Strictly Authored - Zero Unicode / Emoji as Icons)
   ============================================================ */
const IcoArrow = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
  </svg>
);

const IcoPlay = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
    <polygon points="5 3 19 12 5 21 5 3" />
  </svg>
);

const IcoCheck = ({ size = 14, color = "#10B981" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const IcoX = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#DC2626" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

const IcoScan = ({ size = 20, color = "#2563EB" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" />
    <path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" />
    <line x1="7" y1="12" x2="17" y2="12" />
  </svg>
);

const IcoBrain = ({ size = 20, color = "#2563EB" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-4.14z" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-4.14z" />
  </svg>
);

const IcoShield = ({ size = 20, color = "#2563EB" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

const IcoFile = ({ size = 20, color = "#2563EB" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
  </svg>
);

const IcoInfo = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const IcoMenu = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F172A" strokeWidth="2" strokeLinecap="round">
    <line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);

const IcoClose = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F172A" strokeWidth="2" strokeLinecap="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

const IcoHelpCircle = ({ size = 18, color = "#2563EB" }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

/* ============================================================
   LOGO COMPONENT
   Preserves full cyan/blue gradient M-badge in all themes
   ============================================================ */
const Logo = ({ dark = false, height = 44 }: { dark?: boolean; height?: number }) => (
  <a href="#" style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
    {/* eslint-disable-next-line @next/next/no-img-element */}
    <img
      src="/e1697cba-8f8e-4d0b-95ac-bb247a4214be.png"
      alt="MedLens — Scan. Understand. Verify."
      style={{
        height,
        width: "auto",
        objectFit: "contain",
        display: "block",
        filter: dark ? "brightness(0) invert(1)" : "none",
      }}
    />
  </a>
);

/* ============================================================
   HERO PLATFORM SHOWCASE (Clean original image restored)
   ============================================================ */
const HeroPhoneShowcase = () => {
  return (
    <div className="hero-showcase-inner">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/37864170-f174-476b-bf93-96aecfae5e26.png"
        alt="MedLens AI Medicine Scanner & Web Platform"
        className="hero-showcase-img"
      />
    </div>
  );
};

/* ============================================================
   NAVBAR
   ============================================================ */
const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const links = [
    { label: "Home", href: "#" },
    { label: "How it Works", href: "#how-it-works" },
    { label: "Why MedLens", href: "#why-medlens" },
    { label: "Brand Comparison", href: "#brand-comparison" },
    { label: "FAQs", href: "#faqs" },
  ];

  return (
    <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
      <div className="container" style={{ height: 68, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Logo />

        {/* Desktop links */}
        <div style={{ display: "flex", alignItems: "center", gap: 4 }} className="hidden md:flex">
          {links.map((l) => (
            <a
              key={l.label}
              href={l.href}
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: 14,
                fontWeight: 500,
                color: "var(--text-secondary)",
                textDecoration: "none",
                padding: "7px 14px",
                borderRadius: 8,
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLElement;
                el.style.color = "var(--blue)";
                el.style.background = "var(--blue-dim)";
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLElement;
                el.style.color = "var(--text-secondary)";
                el.style.background = "transparent";
              }}
            >
              {l.label}
            </a>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <a href="#scan" className="btn-primary hidden md:inline-flex" style={{ padding: "9px 20px", fontSize: 14 }}>
            Try MedLens <IcoArrow />
          </a>
          <button
            onClick={() => setMobileOpen((o) => !o)}
            style={{ background: "none", border: "none", cursor: "pointer", padding: 6, borderRadius: 6 }}
            className="md:hidden"
            aria-label="Toggle navigation menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <IcoClose /> : <IcoMenu />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div style={{ background: "rgba(255, 255, 255, 0.98)", backdropFilter: "blur(16px)", borderTop: "1px solid var(--border)", padding: "16px 24px 24px", boxShadow: "0 12px 30px rgba(0,0,0,0.08)" }}>
          {links.map((l) => (
            <a
              key={l.label}
              href={l.href}
              onClick={() => setMobileOpen(false)}
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: 14.5,
                fontWeight: 600,
                color: "var(--text-primary)",
                textDecoration: "none",
                display: "block",
                padding: "12px 0",
                borderBottom: "1px solid var(--border)",
              }}
            >
              {l.label}
            </a>
          ))}
          <a href="#scan" className="btn-primary" onClick={() => setMobileOpen(false)} style={{ marginTop: 18, width: "100%", justifyContent: "center" }}>
            Try MedLens <IcoArrow />
          </a>
        </div>
      )}
    </nav>
  );
};

/* ============================================================
   HERO SECTION
   Balanced 3-column feature grid + Clinical Telemetry Proof Strip
   ============================================================ */
const HeroSection = () => (
  <section style={{ paddingTop: 112, paddingBottom: 76, position: "relative", overflow: "hidden", background: "var(--bg)" }}>
    <div className="hero-container">
      <div className="hero-grid">
        
        {/* Left Content Column */}
        <div style={{ maxWidth: 540 }}>
          {/* Clinical Badge */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "5px 12px",
              background: "var(--blue-dim)",
              border: "1px solid var(--blue-border)",
              borderRadius: 999,
              marginBottom: 16,
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--blue)" }} />
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 700, color: "var(--blue)", letterSpacing: "0.04em" }}>
              AI MEDICINE COMPOSITION ANALYZER
            </span>
          </div>

          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(38px, 4.2vw, 58px)",
              fontWeight: 900,
              letterSpacing: "-0.03em",
              lineHeight: 1.08,
              marginBottom: 18,
              color: "#0F172A",
            }}
          >
            Scan.<br />
            <span style={{ color: "var(--blue)" }}>Understand.</span><br />
            Verify.
          </h1>

          <p style={{ fontFamily: "var(--font-body)", fontSize: 16.5, lineHeight: 1.7, color: "var(--text-secondary)", marginBottom: 28 }}>
            Turn a picture of any medicine packaging into clear, verified ingredient breakdowns, active salt dosages, and bioequivalence checks — in seconds.
          </p>

          {/* Balanced 3-Column Pillar Grid (Fixes the P0 Asymmetry Defect) */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 28 }}>
            {[
              { icon: <IcoScan size={18} />, step: "1. Scan", desc: "Strip, box, or bottle" },
              { icon: <IcoBrain size={18} />, step: "2. Understand", desc: "Plain salt breakdown" },
              { icon: <IcoShield size={18} />, step: "3. Verify", desc: "INN reference match" },
            ].map((vp) => (
              <div
                key={vp.step}
                style={{
                  background: "#FFFFFF",
                  border: "1px solid var(--border)",
                  borderRadius: 10,
                  padding: "12px 10px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                  boxShadow: "var(--shadow-sm)",
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 7,
                    background: "var(--blue-dim)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {vp.icon}
                </div>
                <div>
                  <div style={{ fontFamily: "var(--font-heading)", fontSize: 13, fontWeight: 700, color: "#0F172A", marginBottom: 2 }}>
                    {vp.step}
                  </div>
                  <div style={{ fontFamily: "var(--font-body)", fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.35 }}>
                    {vp.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Action CTAs */}
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 16 }}>
            <a href="#scan" className="btn-primary" style={{ fontSize: 15, padding: "12px 26px" }}>
              Try MedLens Now <IcoArrow />
            </a>
            <a href="#how-it-works" className="btn-secondary" style={{ fontSize: 15, padding: "12px 24px" }}>
              <IcoPlay /> Watch Demo
            </a>
          </div>

          {/* Clinical Telemetry Proof Strip (High Social Proof) */}
          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap", padding: "14px 0", borderTop: "1px solid var(--border)", marginTop: 18 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <IcoCheck size={14} color="#10B981" />
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>99.4%</span>
              <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>Salt Precision</span>
            </div>
            <div style={{ width: 1, height: 14, background: "var(--border)" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <IcoCheck size={14} color="#10B981" />
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>10,000+</span>
              <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>INN Drugs</span>
            </div>
            <div style={{ width: 1, height: 14, background: "var(--border)" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <IcoCheck size={14} color="#10B981" />
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>Zero PII</span>
              <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>RAM-Only</span>
            </div>
          </div>

          {/* Legal / Clinical Disclaimer */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 4 }}>
            <IcoInfo />
            <span style={{ fontFamily: "var(--font-body)", fontSize: 11.5, color: "var(--text-muted)" }}>
              Informational tool — not a clinical diagnosis, medical prescription, or dosage advice.
            </span>
          </div>
        </div>

        {/* Right Platform Showcase */}
        <div className="hero-showcase-wrapper">
          <HeroPhoneShowcase />
        </div>
      </div>
    </div>
  </section>
);

/* ============================================================
   THE PROBLEM SECTION
   With Real Image of Pharmaceutical Medicine Carton & Blister Pack
   ============================================================ */
const ProblemSection = () => (
  <section style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
    <div className="container">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 48, alignItems: "center" }}>
        
        {/* Left Column: Context & Pain Points */}
        <div>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(26px, 3.5vw, 40px)",
              fontWeight: 800,
              letterSpacing: "-0.02em",
              marginBottom: 16,
              color: "#0F172A",
            }}
          >
            Medicine packaging is built for chemists, not patients.
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 15.5, color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: 22 }}>
            Medicine boxes are packed with chemical abbreviations, strength ratios, excipients, and regulatory warnings that make it nearly impossible to quickly know what is actually inside your pill.
          </p>

          {/* Pain Point Questions */}
          <div style={{ padding: "18px 20px", borderRadius: 12, background: "var(--surface-alt)", border: "1px solid var(--border)", marginBottom: 22 }}>
            <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--blue-dim)", border: "1.5px solid var(--blue-border)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
              <IcoHelpCircle size={16} color="var(--blue)" />
            </div>
            {[
              "\"What is the active therapeutic chemical vs. inactive binder?\"",
              "\"Is this substitute brand the exact same salt as my prescription?\"",
              "\"Why does the packaging say 'Excipients q.s.'?\"",
            ].map((q) => (
              <div key={q} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                <span style={{ color: "var(--blue)", fontSize: 14, flexShrink: 0 }}>•</span>
                <span style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "var(--text-secondary)", lineHeight: 1.5 }}>{q}</span>
              </div>
            ))}
          </div>

          {/* Tag Pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {["Chemical INN Salts", "Dosage Strengths", "Excipients q.s.", "Schedule H Warnings", "Bioequivalence Parity"].map((tag) => (
              <span
                key={tag}
                style={{
                  padding: "5px 12px",
                  borderRadius: 999,
                  border: "1px solid var(--border)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 11.5,
                  color: "var(--text-secondary)",
                  background: "#fff",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Right Column: Real Medicine Packaging Image */}
        <div style={{ position: "relative", display: "flex", justifyContent: "center", alignItems: "center" }}>
          <div
            style={{
              borderRadius: 18,
              overflow: "hidden",
              border: "1px solid var(--border)",
              boxShadow: "0 16px 40px rgba(15, 23, 42, 0.08)",
              background: "#FFFFFF",
              maxWidth: 400,
              width: "100%",
            }}
          >
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", background: "#FFFFFF", padding: "12px 12px 4px" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/c7f09fc4-8342-46ba-9471-3e4158342213.png"
                alt="Pure Nutrition Multivitamin formulation label showing complex ingredients, active salts, and excipients"
                style={{
                  maxHeight: 390,
                  maxWidth: "100%",
                  height: "auto",
                  width: "auto",
                  display: "block",
                  objectFit: "contain",
                }}
              />
            </div>
            <div style={{ padding: "14px 18px", background: "var(--surface-alt)", borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
              <div>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 13.5, fontWeight: 700, color: "#0F172A" }}>
                  Pure Nutrition Multivitamin
                </div>
                <div style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-secondary)" }}>
                  Dense formulation panel • Active salts, RDA% & Excipients
                </div>
              </div>
              <span style={{ padding: "4px 10px", borderRadius: 999, background: "#FEF2F2", border: "1px solid #FECACA", color: "#DC2626", fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                Complex Label Data
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

/* ============================================================
   THE SOLUTION (DETERMINISTIC VERIFICATION PIPELINE)
   5 Steps Connected with Proper Directional Arrows
   ============================================================ */
const HowItWorksSection = () => {
  const steps = [
    { n: 1, label: "Scan / Upload", icon: <IcoScan size={20} color="#fff" />, items: ["Tablet strip", "Medicine box", "Syrup bottle", "Composition panel"] },
    { n: 2, label: "Extract", icon: <IcoFile size={20} color="#fff" />, items: ["Medicine trade name", "Strengths & dosages", "Prescription marks", "Manufacturer ID"] },
    { n: 3, label: "Identify & Verify", icon: <IcoShield size={20} color="#fff" />, items: ["Canonical INN mapping", "OpenFDA & PubChem", "Bioequivalence check", "Flag unverified claims"] },
    { n: 4, label: "AI Synthesis", icon: <IcoBrain size={20} color="#fff" />, items: ["Active vs inactive roles", "Therapeutic purpose", "Plain-English summary", "Contraindications"] },
    { n: 5, label: "Clinical Report", icon: <IcoFile size={20} color="#fff" />, items: ["Structured clarity", "Confidence telemetry", "Official citations", "Brand delta match"] },
  ];

  return (
    <section id="how-it-works" style={{ padding: "80px 0", background: "var(--bg)", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
            <div>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 8, color: "#0F172A" }}>
                Deterministic Verification Pipeline
              </h2>
              <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 520 }}>
                Every image flows through 5 disciplined verification gates — ensuring zero AI hallucination.
              </p>
            </div>
            <div style={{ padding: "6px 14px", borderRadius: 999, background: "var(--blue-dim)", border: "1px solid var(--blue-border)", color: "var(--blue)", fontSize: 12.5, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
              5-STAGE PIPELINE
            </div>
          </div>
        </div>

        {/* 5-Step Pipeline Flow with Connected Directional Arrows */}
        <div className="pipeline-flow-container">
          {steps.map((step, idx) => (
            <React.Fragment key={step.n}>
              <div
                className="card-hover pipeline-card"
                style={{
                  padding: "20px 16px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  border: "1px solid var(--border)",
                  background: "#FFFFFF",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div className="step-circle">{step.n}</div>
                      <div style={{ width: 32, height: 32, borderRadius: 8, background: "#334155", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        {step.icon}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontFamily: "var(--font-heading)", fontSize: 14.5, fontWeight: 700, marginBottom: 10, color: "#0F172A" }}>
                    {step.label}
                  </div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {step.items.map((item) => (
                      <li key={item} style={{ display: "flex", gap: 6, marginBottom: 6 }}>
                        <span style={{ color: "var(--blue)", marginTop: 2, flexShrink: 0 }}>
                          <IcoCheck size={11} color="var(--blue)" />
                        </span>
                        <span style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                          {item}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Explicit Arrow pointing cleanly to next step */}
              {idx < steps.length - 1 && (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, padding: "4px 0" }}>
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: "var(--blue-dim)",
                      border: "1.5px solid var(--blue-border)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "0 2px 6px rgba(37, 99, 235, 0.12)",
                    }}
                  >
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" className="pipeline-arrow-svg">
                      <line x1="5" y1="12" x2="19" y2="12" />
                      <polyline points="13 6 19 12 13 18" />
                    </svg>
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ============================================================
   WHY MEDLENS (SYNCHRONIZED ROW COMPARISON)
   ============================================================ */
const WhyMedLensSection = () => {
  const tableRows = [
    { label: "Design", ai: "General-purpose conversational chatbot", ml: "Purpose-built for pharmaceutical label analysis" },
    { label: "Input", ai: "User must formulate exact medical prompts", ml: "Image-first — label composition parsed automatically" },
    { label: "Analysis", ai: "Unconstrained text generation (hallucination risk)", ml: "Deterministic entity extraction & INN normalization" },
    { label: "Evidence", ai: "Unverified internal training memory", ml: "Real-time grounding in OpenFDA, PubChem & DailyMed" },
    { label: "Output", ai: "Unstructured conversational paragraphs", ml: "Clinically structured report + confidence telemetry" },
    { label: "Equivalence", ai: "Manual querying brand by brand", ml: "Automated Active Salt & Excipient Delta Matcher" },
  ];

  return (
    <section id="why-medlens" style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
            <div>
              <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 10, color: "#0F172A" }}>
                Built for zero-tolerance medicine verification
              </h2>
              <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 520 }}>
                General AI models are designed for conversational fluency, not clinical correctness. MedLens constrains AI to a deterministic verification layer.
              </p>
            </div>
            <a href="#brand-comparison" style={{ fontFamily: "var(--font-heading)", fontSize: 14, color: "var(--blue)", textDecoration: "none", display: "flex", alignItems: "center", gap: 4, fontWeight: 700 }}>
              See brand comparison <IcoArrow />
            </a>
          </div>
        </div>

        {/* Two-Column Synchronized Comparison */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
          {/* General AI (Left, Light) */}
          <div className="card" style={{ padding: 26 }}>
            <div style={{ minHeight: 80, display: "flex", flexDirection: "column", justifyContent: "center", marginBottom: 20, borderBottom: "1px solid var(--border)", paddingBottom: 14 }}>
              <div style={{ fontFamily: "var(--font-heading)", fontSize: 18, fontWeight: 800, color: "#0F172A", marginBottom: 4 }}>
                General AI
              </div>
              <div style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-muted)" }}>
                Unconstrained Large Language Models (ChatGPT · Gemini · Claude)
              </div>
            </div>
            {tableRows.map((row) => (
              <div key={row.label} style={{ paddingBottom: 12, marginBottom: 12, borderBottom: "1px solid var(--border)", display: "grid", gridTemplateColumns: "100px 1fr", gap: 12 }}>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>{row.label}</div>
                <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span style={{ marginTop: 2, flexShrink: 0 }}><IcoX size={14} /></span>
                  <span style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.45 }}>{row.ai}</span>
                </div>
              </div>
            ))}
          </div>

          {/* MedLens (Right, Dark Sleek) */}
          <div className="ml-dark-card" style={{ padding: 26 }}>
            <div style={{ minHeight: 80, display: "flex", flexDirection: "column", justifyContent: "center", marginBottom: 20, borderBottom: "1px solid rgba(255, 255, 255, 0.10)", paddingBottom: 14 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 4 }}>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 18, fontWeight: 800, color: "#fff" }}>
                  MedLens
                </div>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "#60A5FA", padding: "3px 10px", background: "rgba(37,99,235,0.25)", borderRadius: 999, border: "1px solid rgba(37,99,235,0.35)" }}>
                  Clinical Protocol
                </span>
              </div>
              <div style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "#94A3B8" }}>
                Deterministic Medicine Verification & Normalization Engine
              </div>
            </div>
            {tableRows.map((row) => (
              <div key={row.label} className="ml-check-row">
                <div style={{ width: 20, height: 20, borderRadius: "50%", background: "#2563EB", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <IcoCheck size={11} color="#fff" />
                </div>
                <span>{row.ml}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

/* ============================================================
   BRAND COMPARISON ENGINE (Actionable Price & Allergy Deltas)
   ============================================================ */
const BrandComparisonSection = () => {
  const [selectedPair, setSelectedPair] = useState(0);

  const pairs = [
    {
      title: "Dolo 650 vs. Calpol 650",
      type: "Fever & Analgesic Bioequivalence",
      brandA: { name: "Dolo 650", maker: "Micro Labs", salt: "Paracetamol IP", strength: "650 mg", binders: "Starch, magnesium stearate", price: "₹32 / 15 tabs" },
      brandB: { name: "Calpol 650", maker: "GlaxoSmithKline", salt: "Paracetamol IP", strength: "650 mg", binders: "Microcrystalline cellulose", price: "₹34 / 15 tabs" },
      savingsPill: "Price Parity (₹32 vs ₹34) • Identical therapeutic API",
      allergyCheck: "Allergen Discrepancy: Zero (Both lactose & gluten-free)",
      verdict: "100% Bioequivalent API Match. Both deliver identical therapeutic antipyretic efficacy. Patients can safely substitute either brand without altering dosage.",
    },
    {
      title: "Augmentin 625 vs. Clavam 625",
      type: "Dual-API Antibiotic Ratio Match",
      brandA: { name: "Augmentin 625 Duo", maker: "GlaxoSmithKline", salt: "Amoxicillin + Clavulanate", strength: "500 mg + 125 mg (4:1)", binders: "Titanium dioxide film coat", price: "₹205 / 10 tabs" },
      brandB: { name: "Clavam 625", maker: "Alkem Laboratories", salt: "Amoxicillin + Clavulanate", strength: "500 mg + 125 mg (4:1)", binders: "Cellulose film coat", price: "₹168 / 10 tabs" },
      savingsPill: "Save ₹37 / strip (-18%) with Clavam 625",
      allergyCheck: "Synergistic 4:1 Ratio Confirmed • Film-coated formulation",
      verdict: "Identical 4:1 synergistic antibiotic formulation. Meets standard pharmacopeial bioequivalence criteria while offering ~18% cost savings.",
    },
    {
      title: "Allegra 120 vs. Fexova 120",
      type: "Antihistamine Active Salt Match",
      brandA: { name: "Allegra 120", maker: "Sanofi India", salt: "Fexofenadine HCl", strength: "120 mg", binders: "Iron oxide pink coating", price: "₹198 / 10 tabs" },
      brandB: { name: "Fexova 120", maker: "Intas Pharma", salt: "Fexofenadine HCl", strength: "120 mg", binders: "Standard film opacifier", price: "₹130 / 10 tabs" },
      savingsPill: "Save ₹68 / strip (-34%) with Fexova 120",
      allergyCheck: "Second-Generation Non-Sedating • Identical H1 receptor binding",
      verdict: "100% INN Identity (Fexofenadine HCl). Non-sedating second-generation antihistamine with identical receptor affinity and safety profile.",
    },
  ];

  const curr = pairs[selectedPair];

  return (
    <section id="brand-comparison" style={{ padding: "80px 0", background: "var(--bg)", borderTop: "1px solid var(--border)" }}>
      <div className="container">
        <div style={{ marginBottom: 36 }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 10, color: "#0F172A" }}>
            Compare Medicine Brands & Generic Substitutes
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 16, color: "var(--text-secondary)", maxWidth: 640 }}>
            Confused when a pharmacist substitutes an alternate brand? MedLens strips trade names, extracts canonical INN chemical salts, and confirms bioequivalence instantly.
          </p>
        </div>

        {/* Pair Selector Tabs */}
        <div style={{ display: "flex", gap: 10, marginBottom: 24, overflowX: "auto", paddingBottom: 6 }}>
          {pairs.map((p, idx) => (
            <button
              key={p.title}
              onClick={() => setSelectedPair(idx)}
              style={{
                padding: "10px 18px",
                borderRadius: 999,
                border: selectedPair === idx ? "1.5px solid var(--blue)" : "1px solid var(--border)",
                background: selectedPair === idx ? "var(--blue)" : "#fff",
                color: selectedPair === idx ? "#fff" : "var(--text-primary)",
                fontFamily: "var(--font-heading)",
                fontSize: 13.5,
                fontWeight: 700,
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.18s ease",
              }}
            >
              {p.title}
            </button>
          ))}
        </div>

        {/* Savings & Clinical Delta Strip */}
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: "#DCFCE7", border: "1px solid #86EFAC", color: "#166534", fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 700, display: "inline-flex", alignItems: "center", gap: 6 }}>
            <IcoCheck size={12} color="#166534" /> {curr.savingsPill}
          </div>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: "var(--surface-blue)", border: "1px solid var(--blue-border)", color: "#1E40AF", fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 700, display: "inline-flex", alignItems: "center", gap: 6 }}>
            <IcoShield size={12} color="#1E40AF" /> {curr.allergyCheck}
          </div>
        </div>

        {/* Comparison Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20, marginBottom: 20 }}>
          {/* Brand A */}
          <div className="card" style={{ padding: 24 }}>
            <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--blue)", fontWeight: 700, textTransform: "uppercase" }}>Brand A (Prescribed)</span>
            <h3 style={{ fontFamily: "var(--font-heading)", fontSize: 20, fontWeight: 800, color: "#0F172A", margin: "4px 0" }}>{curr.brandA.name}</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Mfg: {curr.brandA.maker}</p>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "var(--surface-alt)", marginBottom: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Active Salt & Strength</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#0F172A", fontFamily: "var(--font-mono)" }}>{curr.brandA.salt} {curr.brandA.strength}</div>
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 8 }}>Binders: {curr.brandA.binders}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0F172A" }}>Market Price: {curr.brandA.price}</div>
          </div>

          {/* Brand B */}
          <div className="card" style={{ padding: 24 }}>
            <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--green)", fontWeight: 700, textTransform: "uppercase" }}>Brand B (Generic Substitute)</span>
            <h3 style={{ fontFamily: "var(--font-heading)", fontSize: 20, fontWeight: 800, color: "#0F172A", margin: "4px 0" }}>{curr.brandB.name}</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Mfg: {curr.brandB.maker}</p>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "var(--surface-alt)", marginBottom: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Active Salt & Strength</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#0F172A", fontFamily: "var(--font-mono)" }}>{curr.brandB.salt} {curr.brandB.strength}</div>
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 8 }}>Binders: {curr.brandB.binders}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0F172A" }}>Market Price: {curr.brandB.price}</div>
          </div>
        </div>

        {/* Verdict Banner */}
        <div style={{ padding: "18px 22px", borderRadius: 12, background: "var(--surface-blue)", border: "1px solid var(--blue-border)", display: "flex", alignItems: "flex-start", gap: 14 }}>
          <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#10B981", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 2 }}>
            <IcoCheck size={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 14, fontWeight: 700, color: "#1E3A8A", marginBottom: 3 }}>
              MedLens Bioequivalence Verdict: 100% Active Molecule Parity
            </div>
            <p style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "#334155", lineHeight: 1.5 }}>
              {curr.verdict}
            </p>
          </div>
        </div>

        {/* Authoritative Databases Grounding Strip */}
        <div style={{ marginTop: 36, paddingTop: 24, borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
          <span style={{ fontSize: 11.5, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Grounded in Authoritative Databases:
          </span>
          <div style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
            {["OpenFDA", "PubChem (NLM)", "DailyMed (NIH)", "WHO Essential Medicines", "Indian Pharmacopoeia (IP)"].map((std) => (
              <span key={std} style={{ fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 600, color: "var(--text-secondary)", display: "inline-flex", alignItems: "center", gap: 5 }}>
                <IcoCheck size={12} color="#2563EB" /> {std}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

/* ============================================================
   FAQ SECTION (With Full ARIA Accessibility)
   ============================================================ */
const FAQSection = () => {
  const [open, setOpen] = useState<number | null>(0);
  const faqs = [
    {
      cat: "Clinical Safety",
      q: "Is MedLens a diagnostic tool?",
      a: "No. MedLens is strictly an educational and informational platform. It analyzes medicine packaging text and provides ingredient breakdowns. It never advises taking a medication, adjusting dosages, or diagnosing conditions. Always consult a licensed healthcare professional.",
    },
    {
      cat: "Verification Technology",
      q: "How does MedLens prevent AI hallucinations in medicine data?",
      a: "MedLens uses a deterministic verification pipeline: the LLM is never a medical knowledge source — only a plain-language synthesis formatter (temperature=0.0). Any ingredient or dosage claim in the output that was not verified in the OCR text and reference database is strictly purged. Output schemas are enforced via strict validation.",
    },
    {
      cat: "Privacy & Data",
      q: "Is my uploaded packaging photo stored?",
      a: "No. Images are processed in ephemeral volatile server RAM and discarded immediately after feature extraction. Only a cryptographic SHA-256 hash and extracted text tokens are stored for audit — raw patient or packaging pixels are never persisted.",
    },
    {
      cat: "Verification Technology",
      q: "What sources does MedLens use for verification?",
      a: "MedLens cross-references authoritative sources including OpenFDA, PubChem / National Library of Medicine (NLM), WHO Essential Medicines, and DailyMed. All claims cite their source registry for complete transparency.",
    },
    {
      cat: "Bioequivalence",
      q: "Can MedLens compare two different medicine brands?",
      a: "Yes. The Brand Comparison Engine scans two medicines, normalizes both to their canonical active International Nonproprietary Names (INNs), and highlights active salt equivalence, dosage parity, and excipient differences side by side.",
    },
    {
      cat: "Image Processing",
      q: "What happens if a medicine label is blurry or low quality?",
      a: "The image preprocessing pipeline runs a Laplacian variance blur check. If the image clarity score falls below the threshold (σ² < 100), MedLens rejects the photo and asks you to retake it rather than risk an unreliable OCR extraction.",
    },
  ];

  return (
    <section id="faqs" style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
      <div className="container" style={{ maxWidth: 768 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", color: "#0F172A" }}>
            Frequently Asked Questions
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 15.5, color: "var(--text-secondary)", marginTop: 8 }}>
            Everything you need to know about our clinical verification methodology.
          </p>
        </div>

        {faqs.map((faq, i) => (
          <div key={i} className="faq-item">
            <button
              className="faq-btn"
              onClick={() => setOpen(open === i ? null : i)}
              aria-expanded={open === i}
              aria-controls={`faq-answer-${i}`}
              id={`faq-question-${i}`}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700, color: "var(--blue)", background: "var(--blue-dim)", padding: "2px 6px", borderRadius: 4 }}>
                  {faq.cat}
                </span>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 15.5, fontWeight: 700, color: "#0F172A" }}>
                  {faq.q}
                </span>
              </div>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  flexShrink: 0,
                  background: open === i ? "var(--blue)" : "var(--surface-alt)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s",
                  transform: open === i ? "rotate(45deg)" : "none",
                }}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={open === i ? "#fff" : "#475569"} strokeWidth="2.5" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </div>
            </button>
            {open === i && (
              <div className="faq-answer" id={`faq-answer-${i}`} role="region" aria-labelledby={`faq-question-${i}`}>
                <p style={{ fontFamily: "var(--font-body)", fontSize: 14.5, color: "var(--text-secondary)", lineHeight: 1.75 }}>
                  {faq.a}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

/* ============================================================
   SOCIAL ICONS FOR FOOTER
   ============================================================ */
const IcoGithub = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
  </svg>
);

const IcoLinkedIn = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
  </svg>
);

const IcoTwitterX = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const IcoYouTube = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
  </svg>
);

/* ============================================================
   DARK CTA BANNER (Floating Card Matched Exactly to Design Crop)
   ============================================================ */
/* ============================================================
   DARK CTA BANNER (Floating Card - Increased Size & Breathing Room)
   ============================================================ */
const CTASection = () => (
  <section
    id="scan"
    style={{
      padding: "44px 0 24px",
      background: "#ffffff",
    }}
  >
    <div className="container">
      <div
        style={{
          background: "#081024",
          borderRadius: 14,
          border: "1px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 18px 40px rgba(8, 16, 36, 0.25)",
          padding: "24px 34px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 24,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Left tablet blister strip accent */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/real_medicine_tablet.jpg"
          alt=""
          aria-hidden="true"
          style={{
            position: "absolute",
            left: -25,
            top: -22,
            height: 130,
            width: 150,
            objectFit: "cover",
            objectPosition: "right center",
            transform: "rotate(15deg)",
            opacity: 0.28,
            pointerEvents: "none",
            maskImage: "linear-gradient(to right, black 25%, transparent 80%)",
            WebkitMaskImage: "linear-gradient(to right, black 25%, transparent 80%)",
          }}
        />

        {/* Right tablet blister strip accent */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/real_medicine_tablet.jpg"
          alt=""
          aria-hidden="true"
          style={{
            position: "absolute",
            right: -25,
            top: -22,
            height: 130,
            width: 165,
            objectFit: "cover",
            objectPosition: "right center",
            transform: "rotate(-15deg)",
            opacity: 0.38,
            pointerEvents: "none",
            maskImage: "linear-gradient(to left, black 25%, transparent 80%)",
            WebkitMaskImage: "linear-gradient(to left, black 25%, transparent 80%)",
          }}
        />

        {/* Left: White Logo & Headline */}
        <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap", position: "relative", zIndex: 2 }}>
          <Logo dark height={36} />
          <div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(18px, 2.2vw, 22px)", fontWeight: 800, color: "#FFFFFF", letterSpacing: "-0.015em", marginBottom: 4 }}>
              Ready to make medicine information simpler?
            </div>
            <div style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "#94A3B8" }}>
              Scan a medicine label and get a clear, verified explanation — in seconds.
            </div>
          </div>
        </div>

        {/* Right: CTA Buttons */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", position: "relative", zIndex: 2 }}>
          <a href="#scan" className="btn-primary" style={{ padding: "11px 24px", fontSize: 14.5, fontWeight: 700, borderRadius: 9, whiteSpace: "nowrap" }}>
            Try MedLens Now <IcoArrow />
          </a>
          <a
            href="#how-it-works"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "11px 22px",
              border: "1px solid rgba(255, 255, 255, 0.28)",
              borderRadius: 9,
              color: "#FFFFFF",
              fontFamily: "var(--font-heading)",
              fontWeight: 600,
              fontSize: 14.5,
              textDecoration: "none",
              transition: "all 0.15s ease",
              cursor: "pointer",
              whiteSpace: "nowrap",
              background: "rgba(255, 255, 255, 0.04)",
            }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.background = "rgba(255, 255, 255, 0.12)")}
            onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.background = "rgba(255, 255, 255, 0.04)")}
          >
            <IcoPlay /> Watch Demo
          </a>
        </div>
      </div>
    </div>
  </section>
);

/* ============================================================
   FOOTER (Restored Comprehensive Multi-Column Style)
   ============================================================ */
const Footer = () => (
  <footer style={{ background: "#ffffff", borderTop: "1px solid var(--border)", padding: "56px 24px 28px" }}>
    <div className="container">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 40, marginBottom: 40, alignItems: "flex-start" }}>
        {/* Brand Block */}
        <div style={{ maxWidth: 360 }}>
          <Logo height={38} />
          <p style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "var(--text-secondary)", lineHeight: 1.7, marginTop: 16 }}>
            MedLens is an AI-powered medicine composition analyzer that helps patients understand ingredients, verify safety against canonical databases, and compare brand bioequivalence.
          </p>
          <div style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 999, background: "var(--blue-dim)", border: "1px solid var(--blue-border)" }}>
            <span style={{ fontFamily: "var(--font-heading)", fontSize: 12, fontWeight: 700, color: "var(--blue)" }}>
              Complex Medicine Labels. Clear Answers.
            </span>
          </div>
        </div>

        {/* Nav Columns */}
        <div>
          <div style={{ fontFamily: "var(--font-heading)", fontSize: 12, fontWeight: 700, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 14 }}>
            Platform
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
            {["Home", "How it Works", "Why MedLens", "Brand Comparison", "FAQs"].map((l) => (
              <li key={l}>
                <a
                  href={`#${l.toLowerCase().replace(/\s+/g, "-")}`}
                  style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)", textDecoration: "none", transition: "color 0.15s" }}
                  onMouseEnter={(e) => ((e.target as HTMLElement).style.color = "var(--blue)")}
                  onMouseLeave={(e) => ((e.target as HTMLElement).style.color = "var(--text-secondary)")}
                >
                  {l}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div style={{ fontFamily: "var(--font-heading)", fontSize: 12, fontWeight: 700, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 14 }}>
            Sources Cited
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
            {["OpenFDA Drug API", "PubChem / NLM", "DailyMed (NIH)", "WHO Essential Medicines", "Indian Pharmacopoeia (IP)"].map((l) => (
              <li key={l}>
                <span style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)" }}>
                  {l}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div style={{ fontFamily: "var(--font-heading)", fontSize: 12, fontWeight: 700, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 14 }}>
            Clinical & Privacy
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
            {["Zero-PII Storage Policy", "Ephemeral Volatile RAM", "Non-Prescription Boundary", "Deterministic OCR Verification", "Terms of Service"].map((l) => (
              <li key={l}>
                <span style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)" }}>
                  {l}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: "var(--border)", marginBottom: 20 }} />

      {/* Bottom Bar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <span style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-muted)" }}>
          © {new Date().getFullYear()} MedLens. All rights reserved.
        </span>
        <p style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-muted)", textAlign: "center" }}>
          Informational tool — not a clinical diagnosis, medical advice, or prescription.
        </p>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", gap: 16 }}>
            {["Privacy Policy", "Clinical Disclaimer", "Contact"].map((l) => (
              <a
                key={l}
                href="#"
                style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-muted)", textDecoration: "none", transition: "color 0.15s" }}
                onMouseEnter={(e) => ((e.target as HTMLElement).style.color = "var(--blue)")}
                onMouseLeave={(e) => ((e.target as HTMLElement).style.color = "var(--text-muted)")}
              >
                {l}
              </a>
            ))}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginLeft: 8 }}>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              style={{ color: "#64748B", display: "inline-flex", alignItems: "center", transition: "color 0.15s ease" }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "var(--blue)")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#64748B")}
            >
              <IcoGithub />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
              style={{ color: "#64748B", display: "inline-flex", alignItems: "center", transition: "color 0.15s ease" }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "var(--blue)")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#64748B")}
            >
              <IcoLinkedIn />
            </a>
            <a
              href="https://x.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="X (Twitter)"
              style={{ color: "#64748B", display: "inline-flex", alignItems: "center", transition: "color 0.15s ease" }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "var(--blue)")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#64748B")}
            >
              <IcoTwitterX />
            </a>
            <a
              href="https://youtube.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="YouTube"
              style={{ color: "#64748B", display: "inline-flex", alignItems: "center", transition: "color 0.15s ease" }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = "var(--blue)")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = "#64748B")}
            >
              <IcoYouTube />
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
);

/* ============================================================
   MAIN PAGE EXPORT
   ============================================================ */
export default function HomePage() {
  return (
    <main>
      <Navbar />
      <HeroSection />
      <ProblemSection />
      <HowItWorksSection />
      <WhyMedLensSection />
      <BrandComparisonSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </main>
  );
}
