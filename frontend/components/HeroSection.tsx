import React, { useEffect, useRef } from "react";
import { ScrollReveal } from "./ScrollReveal";
import { IcoArrow, IcoPlay, IcoCheck, IcoInfo, IcoScan, IcoBrain, IcoShield } from "./Icons";

/* ============================================================
   HERO PLATFORM SHOWCASE
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
   STAT STRIP — Animated pop-in for social proof numbers
   ============================================================ */
const StatStrip = () => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const items = el.querySelectorAll<HTMLElement>(".stat-item");

    if (prefersReduced) {
      items.forEach((item) => { item.style.opacity = "1"; });
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          items.forEach((item, i) => {
            setTimeout(() => item.classList.add("counted"), i * 130);
          });
          observer.disconnect();
        }
      },
      { threshold: 0.5 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const stats = [
    { value: "99.4%", label: "Salt Precision" },
    { value: "10,000+", label: "INN Drugs" },
    { value: "Zero PII", label: "RAM-Only" },
  ];

  return (
    <div
      ref={ref}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        flexWrap: "wrap",
        padding: "14px 0",
        borderTop: "1px solid var(--border)",
        marginTop: 18,
      }}
    >
      {stats.map((s, i) => (
        <React.Fragment key={s.value}>
          {i > 0 && <div style={{ width: 1, height: 14, background: "var(--border)" }} />}
          <div className="stat-item" style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <IcoCheck size={14} color="#10B981" />
            <span style={{ fontFamily: "var(--font-heading)", fontSize: 12.5, fontWeight: 700, color: "#0F172A" }}>
              {s.value}
            </span>
            <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>{s.label}</span>
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};

/* ============================================================
   HERO SECTION
   ============================================================ */
export const HeroSection = () => (
  <section style={{ paddingTop: 112, paddingBottom: 76, position: "relative", overflow: "hidden", background: "var(--bg)" }}>
    {/* Ambient gradient mesh orbs */}
    <div className="hero-orb hero-orb-1" aria-hidden="true" />
    <div className="hero-orb hero-orb-2" aria-hidden="true" />
    <div className="hero-orb hero-orb-3" aria-hidden="true" />

    <div className="hero-container" style={{ position: "relative", zIndex: 1 }}>
      <div className="hero-grid">
        
        {/* Left Content Column */}
        <div style={{ maxWidth: 540 }}>
          {/* Clinical Badge — pops in on load */}
          <div
            className="hero-badge-anim"
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

          {/* H1 — each word slides up independently */}
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(38px, 4.2vw, 58px)",
              fontWeight: 700, // Space Grotesk max is 700
              WebkitTextStroke: "1.5px currentColor", // Thicken the font artificially
              letterSpacing: "-0.035em",
              lineHeight: 1.08,
              marginBottom: 18,
              color: "#0F172A",
            }}
          >
            <span className="hero-word hero-word-1">Scan.</span><br />
            <span className="hero-word hero-word-2" style={{ color: "var(--blue)" }}>Understand.</span><br />
            <span className="hero-word hero-word-3">Verify.</span>
          </h1>

          <p style={{ fontFamily: "var(--font-body)", fontSize: 16.5, lineHeight: 1.7, color: "var(--text-secondary)", marginBottom: 28 }}>
            Turn a photo of any medicine packaging into a clear ingredient breakdown, salt dosages, and brand substitution check — in seconds.
          </p>

          {/* Balanced 3-Column Pillar Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 28 }}>
            {[
              { icon: <IcoScan size={18} />, step: "1. Scan", desc: "Strip, box, or bottle" },
              { icon: <IcoBrain size={18} />, step: "2. Understand", desc: "Plain salt breakdown" },
              { icon: <IcoShield size={18} />, step: "3. Verify", desc: "INN reference match" },
            ].map((vp, i) => (
              <ScrollReveal key={vp.step} variant="fade-up" delay={120 + i * 100} duration={550}>
                <div
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
              </ScrollReveal>
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

          {/* Clinical Telemetry Proof Strip — animated pop-in on load */}
          <StatStrip />


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
