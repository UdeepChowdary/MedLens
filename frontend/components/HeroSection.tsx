import React from "react";
import Link from "next/link";
import { IcoArrow, IcoInfo, IcoScan, IcoBrain, IcoShield } from "./Icons";

/* ============================================================
   HERO PLATFORM SHOWCASE
   Laptop and mobile device mockup showing MedLens app interface
   ============================================================ */
const HeroPhoneShowcase = () => {
  return (
    <div className="hero-showcase-inner">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/37864170-f174-476b-bf93-96aecfae5e26.png"
        alt="MedLens Medicine Scanner and Web Platform"
        className="hero-showcase-img"
      />
    </div>
  );
};

/* ============================================================
   HERO SECTION
   ============================================================ */
export const HeroSection = () => (
  <section style={{ paddingTop: 104, paddingBottom: 72, position: "relative", overflow: "hidden", background: "var(--bg)", borderBottom: "1px solid var(--border)" }}>
    <div className="hero-container" style={{ position: "relative", zIndex: 1 }}>
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
              borderRadius: 6,
              marginBottom: 16,
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--blue)" }} />
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 700, color: "var(--blue)", letterSpacing: "0.04em" }}>
              PHARMACEUTICAL COMPOSITION VERIFICATION
            </span>
          </div>

          {/* Precise, Non-Vague Clinical H1 */}
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(34px, 3.8vw, 48px)",
              fontWeight: 800,
              letterSpacing: "-0.03em",
              lineHeight: 1.15,
              marginBottom: 16,
              color: "#0F172A",
            }}
          >
            Verify Active Pharmaceutical Salts and Packaging Composition
          </h1>

          <p style={{ fontFamily: "var(--font-body)", fontSize: 16, lineHeight: 1.7, color: "var(--text-secondary)", marginBottom: 28 }}>
            Extract active therapeutic chemicals, identify formulation binders, compare brand bioequivalence, and cross-reference authoritative pharmacopeial registries directly from physical blister strips, boxes, and bottles.
          </p>

          {/* 3-Pillar Technical Workflow */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 28 }}>
            {[
              { icon: <IcoScan size={18} />, step: "1. Capture", desc: "Strip, carton, or vial" },
              { icon: <IcoBrain size={18} />, step: "2. Normalize", desc: "Canonical INN salts" },
              { icon: <IcoShield size={18} />, step: "3. Ground", desc: "OpenFDA and PubChem" },
            ].map((vp) => (
              <div
                key={vp.step}
                style={{
                  background: "#FFFFFF",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
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
                    borderRadius: 6,
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
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
            <Link href="/dashboard/scan" className="btn-primary" style={{ fontSize: 14.5, padding: "12px 24px", borderRadius: 6 }}>
              Launch Scanner <IcoArrow />
            </Link>
            <a href="#brand-comparison" className="btn-secondary" style={{ fontSize: 14.5, padding: "12px 22px", borderRadius: 6 }}>
              Compare Brand Formulations
            </a>
          </div>

          {/* Legal / Clinical Disclaimer */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 6 }}>
            <IcoInfo />
            <span style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--text-secondary)" }}>
              Informational tool: not a clinical diagnosis, medical prescription, or dosage recommendation.
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
