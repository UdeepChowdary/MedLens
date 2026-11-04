"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Logo } from "./Logo";
import { IcoArrow, IcoClose, IcoMenu } from "./Icons";
import { useAuth } from "@/context/AuthContext";

export const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();

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

  const scannerHref = user ? "/dashboard/scan" : "/login?redirect=/dashboard/scan";

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
          {user ? (
            <Link
              href="/dashboard"
              style={{
                fontSize: 13.5,
                fontWeight: 600,
                color: "var(--text-primary)",
                textDecoration: "none",
                padding: "8px 14px",
                borderRadius: 6,
                border: "1px solid var(--border)",
                backgroundColor: "white",
              }}
              className="hidden md:inline-flex hover:bg-slate-50 transition-colors"
            >
              Dashboard
            </Link>
          ) : (
            <Link
              href="/login"
              style={{
                fontSize: 13.5,
                fontWeight: 600,
                color: "var(--text-primary)",
                textDecoration: "none",
                padding: "8px 14px",
                borderRadius: 6,
                border: "1px solid var(--border)",
                backgroundColor: "white",
              }}
              className="hidden md:inline-flex hover:bg-slate-50 transition-colors"
            >
              Sign In
            </Link>
          )}

          <Link
            href={scannerHref}
            className="btn-primary hidden md:inline-flex"
            style={{ padding: "8px 18px", fontSize: 13.5, borderRadius: 6, textDecoration: "none" }}
          >
            Launch Scanner <IcoArrow />
          </Link>

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

          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 18 }}>
            {user ? (
              <Link
                href="/dashboard"
                onClick={() => setMobileOpen(false)}
                style={{
                  width: "100%",
                  textAlign: "center",
                  padding: "10px",
                  borderRadius: 6,
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  fontWeight: 600,
                  fontSize: 14,
                  textDecoration: "none",
                }}
              >
                Go to Dashboard
              </Link>
            ) : (
              <Link
                href="/login"
                onClick={() => setMobileOpen(false)}
                style={{
                  width: "100%",
                  textAlign: "center",
                  padding: "10px",
                  borderRadius: 6,
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  fontWeight: 600,
                  fontSize: 14,
                  textDecoration: "none",
                }}
              >
                Sign In
              </Link>
            )}

            <Link
              href={scannerHref}
              className="btn-primary"
              onClick={() => setMobileOpen(false)}
              style={{ width: "100%", justifyContent: "center", borderRadius: 6, textDecoration: "none" }}
            >
              Launch Scanner <IcoArrow />
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
