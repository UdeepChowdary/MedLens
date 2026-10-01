import React from "react";
import { Logo } from "./Logo";
import { IcoArrow, IcoPlay } from "./Icons";

export const CTASection = () => (
  <section
    id="scan"
    style={{
      padding: "44px 0 24px",
      background: "#ffffff",
    }}
  >
    <div className="container">
      <div
        className="cta-glow-border"
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
