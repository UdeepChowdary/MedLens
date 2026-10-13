import React from "react";
import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Footer } from "@/components/Footer";

export const metadata = {
  title: "Terms and Conditions | MedLens Clinical Terms of Service",
  description: "Terms and conditions, non-diagnostic boundaries, and clinical disclaimers governing the use of the MedLens medicine composition platform.",
};

export default function TermsPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "var(--surface)" }}>
      {/* Navigation Header */}
      <header style={{ padding: "18px 32px", borderBottom: "1px solid var(--border)", background: "#ffffff" }}>
        <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Link href="/" style={{ textDecoration: "none" }}>
            <Logo />
          </Link>
          <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
            <Link href="/" style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", textDecoration: "none" }}>
              Back to Overview
            </Link>
            <Link href="/privacy" style={{ fontSize: "14px", fontWeight: 600, color: "var(--blue)", textDecoration: "none" }}>
              Privacy Policy
            </Link>
          </div>
        </div>
      </header>

      {/* Main Legal Content Container */}
      <main style={{ flex: 1, padding: "56px 24px" }}>
        <div className="container" style={{ maxWidth: "860px" }}>
          <div style={{ background: "#ffffff", border: "1px solid var(--border)", borderRadius: "10px", padding: "48px 40px", boxShadow: "var(--shadow-sm)" }}>
            
            <div style={{ marginBottom: "32px", borderBottom: "1px solid var(--border)", paddingBottom: "24px" }}>
              <div style={{ display: "inline-block", fontSize: "11px", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--blue)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "8px" }}>
                Regulatory Boundary & User Terms
              </div>
              <h1 style={{ fontSize: "32px", fontWeight: 800, color: "#0F172A", letterSpacing: "-0.02em", marginBottom: "12px" }}>
                Terms and Conditions
              </h1>
              <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
                Effective Date: October 12, 2026 | Document ID: ML-LEGAL-TOS-03
              </p>
            </div>

            {/* Critical Clinical Alert Box */}
            <div style={{ background: "#FEF2F2", border: "1.5px solid #FCA5A5", borderRadius: "8px", padding: "20px 24px", marginBottom: "32px" }}>
              <div style={{ fontSize: "13px", fontWeight: 800, color: "#991B1B", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "6px" }}>
                Mandatory Clinical Notice: Non-Diagnostic Informational Boundary
              </div>
              <p style={{ fontSize: "14px", color: "#7F1D1D", lineHeight: 1.6, margin: 0 }}>
                MedLens is an informational reference utility and pharmaceutical label transcription tool. It does not provide medical diagnoses, treatment plans, clinical advice, or prescription guidance. MedLens is never a replacement for consultation with a licensed physician, registered medical practitioner, or licensed pharmacist. If you are experiencing a medical emergency, contact your local emergency services immediately.
              </p>
            </div>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                1. Acceptance of Terms
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                By accessing, browsing, or utilizing the MedLens platform, software APIs, or client verification applications, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions and our Privacy Policy. If you do not accept these terms in their entirety, you must discontinue using MedLens immediately.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                2. Scope of Service and Educational Intent
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens provides algorithmic extraction, salt normalization, and database cross-referencing of text printed on commercial pharmaceutical packaging. The platform assists consumers, caregivers, and students in distinguishing active pharmaceutical ingredients (APIs) from formulation excipients and reviewing authoritative pharmacopeial monographs.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                MedLens does not evaluate individual patient health histories, kidney or hepatic impairment profiles, drug-drug synergies in polypharmacy regimes, or allergic responses. All information is presented strictly for reference and comparative education.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                3. Optical Character Recognition and Data Limitations
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                While MedLens applies spatial image preprocessing, contrast enhancement, and multi-gate normalization, OCR technology is inherently subject to optical constraints. Physical packaging wear, metallic foil curvature, reflections, printing errors, or inadequate camera lighting may result in transcription discrepancies or unverified ingredient alerts.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                You agree to inspect the physical packaging, verify printed dosage strengths directly against your written doctor prescription, and seek clarification from your dispensing pharmacist whenever any uncertainty or ambiguity arises.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                4. Brand Comparison and Generic Substitution Protocol
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                The Brand Comparison Engine indicates whether commercial products share the same canonical International Nonproprietary Name (INN) active salt and identifies dosage strength deltas. This analysis is purely mathematical and descriptive. Users must never substitute, omit, double-dose, or modify prescribed medications without explicit authorization from their treating healthcare provider.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                5. Permitted Use and Restrictions
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                You agree to use MedLens solely for legitimate personal reference or academic study. You shall not:
              </p>
              <ul style={{ paddingLeft: "24px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75 }}>
                <li>Submit unlawful, fraudulent, defamatory, or abusive imagery</li>
                <li>Attempt to bypass optical rate-limiting filters or server security barriers</li>
                <li>Rely on MedLens as a primary clinical decision support system in clinical triage</li>
                <li>Scrape, reverse engineer, or systematically extract normalized database entries for commercial resale</li>
              </ul>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                6. Limitation of Liability
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                To the fullest extent permitted by applicable law, MedLens, its developers, contributors, and affiliated research entities shall not be held liable for any direct, indirect, incidental, consequential, or punitive damages arising from the use of, or inability to use, this application; transcription errors; dosage misinterpretations; or adverse drug events resulting from self-medication decisions.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                7. Modifications to Terms
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                We reserve the right to revise and update these Terms and Conditions periodically to maintain clinical and regulatory alignment. Continued access to MedLens following the publication of revised terms constitutes full acceptance of the updated provisions.
              </p>
            </section>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
