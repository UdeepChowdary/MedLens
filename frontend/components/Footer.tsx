import React from "react";
import { Logo } from "./Logo";
import { IcoGithub, IcoLinkedIn, IcoTwitterX, IcoYouTube } from "./Icons";

export const Footer = () => (
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
            {[
              { label: "OpenFDA Drug API", href: "https://open.fda.gov" },
              { label: "PubChem / NLM", href: "https://pubchem.ncbi.nlm.nih.gov" },
              { label: "DailyMed (NIH)", href: "https://dailymed.nlm.nih.gov" },
              { label: "WHO Essential Medicines", href: "https://www.who.int/groups/expert-committee-on-selection-and-use-of-essential-medicines/essential-medicines-lists" },
              { label: "Indian Pharmacopoeia (IP)", href: "https://www.ipc.gov.in" },
            ].map((l) => (
              <li key={l.label}>
                <a
                  href={l.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-secondary)", textDecoration: "none", transition: "color 0.15s" }}
                  onMouseEnter={(e) => ((e.target as HTMLElement).style.color = "var(--blue)")}
                  onMouseLeave={(e) => ((e.target as HTMLElement).style.color = "var(--text-secondary)")}
                >
                  {l.label}
                </a>
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
