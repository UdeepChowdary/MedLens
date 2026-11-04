import React from "react";
import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Footer } from "@/components/Footer";

export const metadata = {
  title: "Terms and Conditions | MedLens Clinical Terms of Service",
  description: "Terms and conditions, non-diagnostic boundaries, personalized safety disclaimers, and clinical usage rules for MedLens.",
};

export default function TermsPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "var(--surface)" }}>
      {/* Navigation Header */}
      <header style={{ padding: "18px 32px", borderBottom: "1px solid var(--border)", background: "#ffffff" }}>
        <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Logo />
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
                Regulatory Boundary &amp; User Terms
              </div>
              <h1 style={{ fontSize: "32px", fontWeight: 800, color: "#0F172A", letterSpacing: "-0.02em", marginBottom: "12px" }}>
                Terms and Conditions
              </h1>
              <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
                Effective Date: November 2026 | Document ID: ML-LEGAL-TOS-04
              </p>
            </div>

            {/* Critical Clinical Alert Box */}
            <div id="clinical-notice" style={{ background: "#FEF2F2", border: "1.5px solid #FCA5A5", borderRadius: "8px", padding: "20px 24px", marginBottom: "32px", scrollMarginTop: "90px" }}>
              <div style={{ fontSize: "13px", fontWeight: 800, color: "#991B1B", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "6px" }}>
                Mandatory Clinical Notice: Non-Diagnostic Informational Boundary
              </div>
              <p style={{ fontSize: "14px", color: "#7F1D1D", lineHeight: 1.6, margin: 0 }}>
                MedLens is an informational reference utility and pharmaceutical packaging analysis tool. It does not provide medical diagnoses, treatment plans, clinical prescriptions, or binding pharmacological advice. MedLens is never a substitute for direct consultation with a qualified medical doctor, licensed physician, or registered pharmacist. If you are experiencing an adverse drug reaction or medical emergency, contact your local emergency services immediately.
              </p>
            </div>

            <section id="acceptance-of-terms" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                1. Acceptance of Terms
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                By accessing, browsing, or utilizing the MedLens platform, packaging scanner, disease comparator, or verification services, you acknowledge that you have read, understood, and agreed to be bound by these Terms and Conditions and our Privacy Policy. If you do not accept these terms in their entirety, you must discontinue using MedLens immediately.
              </p>
            </section>

            <section id="scope-of-service" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                2. Scope of Service &amp; Educational Intent
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens provides algorithmic text extraction, pharmaceutical salt normalization, and regulatory database cross-referencing from commercial medicine packaging. The platform assists patients, consumers, and caregivers in identifying active pharmaceutical ingredients (APIs), understanding formulation binders, and inspecting official monographs (openFDA, PubChem, Indian Pharmacopoeia).
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                All generated reports, confidence indicators, and brand comparisons are presented exclusively for reference and consumer education.
              </p>
            </section>

            {/* Section 3: Personalized Health & BYOK AI Boundaries */}
            <section id="personalized-safety" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                3. Personalized Health Profiles &amp; Bring Your Own Key (BYOK) AI
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens allows users to document known drug allergies (e.g. penicillin, NSAIDs) and medical conditions (e.g. GERD, hypertension) to cross-check against scanned medications. Users may also optionally connect their own Google Gemini API key:
              </p>
              <ul style={{ paddingLeft: "24px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75 }}>
                <li>
                  <strong>Informational Advisory Only:</strong> AI personalized consultations provide supplemental cross-reactivity warnings based on clinical pharmacology models. They do not constitute an individualized physician consultation or guarantee of pharmacological tolerability.
                </li>
                <li>
                  <strong>Independent Verification:</strong> Users must always verify potential drug allergies and contraindications directly with their prescribing physician or dispensing pharmacist before ingesting any new medication.
                </li>
                <li>
                  <strong>User Responsibility for API Keys:</strong> You are solely responsible for maintaining the confidentiality and usage quotas of your Google Gemini API key.
                </li>
              </ul>
            </section>

            <section id="ocr-limitations" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                4. Optical Character Recognition (OCR) &amp; Physical Packaging Constraints
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                While MedLens applies Laplacian blur filtering, high-contrast binarization, and INN dictionary matching, optical character recognition is inherently dependent on physical image conditions. Foil glare, metallic blisters, rounded bottles, curved text, or damaged packaging may lead to unverified salts or extraction gaps.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Users must verify printed dosages directly against the physical packaging and doctor prescription, seeking pharmacist clarification whenever text ambiguity exists.
              </p>
            </section>

            <section id="brand-comparison" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                5. Brand Comparison &amp; Generic Substitution Protocol
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                The Brand &amp; Disease Comparison Engine evaluates whether commercial formulations share identical canonical INN salts, dosage strengths, and binder classes. This comparison is descriptive and educational. You must never substitute, discontinue, or alter prescribed medications without explicit clearance from your healthcare practitioner.
              </p>
            </section>

            <section id="permitted-use" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                6. Permitted Use &amp; User Conduct
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                You agree to use MedLens solely for lawful personal informational reference or academic review. You shall not:
              </p>
              <ul style={{ paddingLeft: "24px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75 }}>
                <li>Submit fraudulent, abusive, or non-pharmaceutical imagery</li>
                <li>Attempt to reverse-engineer, exploit, or bypass optical security boundaries</li>
                <li>Rely on MedLens as a primary clinical decision support system in critical care</li>
                <li>Scrape or mass-extract normalized database entries for unauthorized commercial resale</li>
              </ul>
            </section>

            <section id="liability" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                7. Limitation of Liability
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                To the fullest extent permitted by applicable law, MedLens, its authors, developers, and contributors shall not be held liable for any direct, indirect, incidental, or consequential damages resulting from the use of, or inability to use, this service; optical transcription errors; dosage misinterpretations; or adverse drug events resulting from self-medication decisions.
              </p>
            </section>

            <section id="modifications">
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                8. Modifications to Terms
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                We reserve the right to revise these Terms and Conditions periodically to maintain clinical, legal, and regulatory alignment. Continued access to MedLens following the publication of revised terms constitutes full acceptance of the updated provisions.
              </p>
            </section>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
