import React from "react";
import Link from "next/link";
import { Logo } from "./Logo";
import { IcoArrow } from "./Icons";

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
        style={{
          background: "radial-gradient(ellipse at 50% 0%, #0C1A36 0%, #081024 75%)",
          borderRadius: 14,
          border: "1px solid rgba(255, 255, 255, 0.14)",
          boxShadow: "0 18px 40px rgba(8, 16, 36, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.12)",
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
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: 240,
            pointerEvents: "none",
            overflow: "hidden",
            maskImage: "linear-gradient(to right, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.25) 40%, rgba(0,0,0,0.08) 70%, transparent 100%), linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to right, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.25) 40%, rgba(0,0,0,0.08) 70%, transparent 100%), linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%)",
            maskComposite: "intersect",
            WebkitMaskComposite: "source-in",
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/real_medicine_tablet.jpg"
            alt=""
            style={{
              position: "absolute",
              left: -15,
              top: -20,
              height: 145,
              width: 180,
              objectFit: "cover",
              objectPosition: "center",
              transform: "rotate(14deg)",
              opacity: 0.28,
            }}
          />
        </div>

        {/* Right tablet blister strip accent */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            right: 0,
            top: 0,
            bottom: 0,
            width: 240,
            pointerEvents: "none",
            overflow: "hidden",
            maskImage: "linear-gradient(to left, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.25) 40%, rgba(0,0,0,0.08) 70%, transparent 100%), linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to left, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.25) 40%, rgba(0,0,0,0.08) 70%, transparent 100%), linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%)",
            maskComposite: "intersect",
            WebkitMaskComposite: "source-in",
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/real_medicine_tablet.jpg"
            alt=""
            style={{
              position: "absolute",
              right: -15,
              top: -20,
              height: 145,
              width: 180,
              objectFit: "cover",
              objectPosition: "center",
              transform: "rotate(-14deg) scaleX(-1)",
              opacity: 0.28,
            }}
          />
        </div>


        {/* Left: White Logo & Headline */}
        <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap", position: "relative", zIndex: 2 }}>
          <Logo dark height={36} />
          <div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(18px, 2.2vw, 22px)", fontWeight: 800, color: "#FFFFFF", letterSpacing: "-0.015em", marginBottom: 4 }}>
              Ready to verify medicine compositions?
            </div>
            <div style={{ fontFamily: "var(--font-body)", fontSize: 13.5, color: "#94A3B8" }}>
              Scan a medicine label and get a clear, verified explanation in seconds.
            </div>
          </div>
        </div>

        {/* Right: CTA Buttons */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", position: "relative", zIndex: 2 }}>
          <Link href="/dashboard/scan" className="btn-primary" style={{ padding: "11px 24px", fontSize: 14.5, fontWeight: 700, borderRadius: 6, whiteSpace: "nowrap" }}>
            Launch Scanner <IcoArrow />
          </Link>
        </div>
      </div>
    </div>
  </section>
);
