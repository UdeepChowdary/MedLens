import React, { useState, useEffect } from "react";
import { Logo } from "./Logo";
import { IcoArrow, IcoClose, IcoMenu } from "./Icons";

export const Navbar = () => {
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
