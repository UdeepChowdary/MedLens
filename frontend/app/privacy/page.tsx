import React from "react";
import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Footer } from "@/components/Footer";

export const metadata = {
  title: "Privacy Policy | MedLens Clinical Data Governance",
  description: "MedLens data handling standards, zero-PII architecture, ephemeral processing, and BYOK Gemini API key privacy policies.",
};

export default function PrivacyPage() {
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
            <Link href="/terms" style={{ fontSize: "14px", fontWeight: 600, color: "var(--blue)", textDecoration: "none" }}>
              Terms of Service
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
                Data Architecture &amp; Clinical Privacy Governance
              </div>
              <h1 style={{ fontSize: "32px", fontWeight: 800, color: "#0F172A", letterSpacing: "-0.02em", marginBottom: "12px" }}>
                Privacy Policy
              </h1>
              <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
                Effective Date: November 2026 | Document ID: ML-SEC-POL-05
              </p>
            </div>

            {/* Section 1: Ephemeral Processing */}
            <section id="ephemeral-processing" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                1. Fundamental Operating Principle: Ephemeral Processing
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens operates as an informational pharmaceutical composition verification engine. We adhere to a strict ephemeral processing architecture: physical medicine packaging photos submitted for optical character recognition and salt normalization are held strictly in temporary volatile memory (RAM).
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Uploaded images are immediately purged upon completion of the feature extraction pipeline. We do not store, catalog, train public models on, or persist raw image pixels to persistent disk storage, object buckets, or external third-party repositories.
              </p>
            </section>

            {/* Section 2: Zero-PII */}
            <section id="zero-pii" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                2. Zero-PII Packaging Boundary &amp; Automated Redaction
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens is engineered exclusively to parse printed medicine blister packs, boxes, bottles, and composition inserts. Our packaging intake pipeline does not extract or retain Protected Health Information (PHI) or personal patient identifiers.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                In the event that an uploaded image inadvertently contains human faces, prescription receipts, patient names, or hospital stickers, automated spatial filters apply black bounding redaction masks across those regions prior to tokenization, ensuring non-medicinal elements are completely discarded.
              </p>
            </section>

            {/* Section 3: BYOK Gemini & Health Profile Privacy */}
            <section id="byok-privacy" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                3. Bring Your Own Key (BYOK) &amp; Health Profile Governance
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                To unlock personalized clinical cross-reactivity and contraindication assessments, MedLens offers an optional Bring Your Own Key (BYOK) architecture with Google Gemini:
              </p>
              <ul style={{ paddingLeft: "24px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75, marginBottom: "12px" }}>
                <li>
                  <strong>Client-Side Storage:</strong> Your Gemini API key and documented health conditions/allergies are stored exclusively within your local browser storage (<code>localStorage</code>) on your personal device.
                </li>
                <li>
                  <strong>No Server Key Persistence:</strong> MedLens servers never save, database-persist, or log your Gemini API key. It is transmitted in-memory over encrypted TLS solely to fulfill the requested consultation.
                </li>
                <li>
                  <strong>Direct Provider Integration:</strong> When you execute an AI-enhanced personalized consultation, your key communicates with Google&apos;s official Gemini API endpoints. Google does not use paid or standard API key calls to train base models.
                </li>
                <li>
                  <strong>Full User Control:</strong> You can edit, modify, or permanently delete your stored API key, documented allergies, and pre-existing conditions at any time with one click from the Scan page or Profile page.
                </li>
              </ul>
            </section>

            {/* Section 4: Authentication & User Accounts */}
            <section id="auth-privacy" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                4. User Account Governance &amp; Firebase Authentication
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens provides secure account authentication through Firebase Authentication, supporting Google OAuth and verified email/password sign-in.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Account credentials are encrypted using industry-standard identity protocols. We collect only your basic user profile identifier (email address and display name) necessary to authenticate access to your personal scan history and saved reports. We never sell, rent, or trade user profile data to data brokers, insurers, or pharmaceutical advertisers.
              </p>
            </section>

            {/* Section 5: Immutable Audit Telemetry */}
            <section id="audit-telemetry" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                5. Immutable Audit Telemetry &amp; SHA-256 Hashes
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                To support clinical safety verification, auditability, and OCR fidelity benchmarks, our verification pipeline generates a non-reversible cryptographic SHA-256 digest of extracted pharmaceutical text tokens.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                The persistent audit log contains solely:
              </p>
              <ul style={{ paddingLeft: "24px", marginTop: "8px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75 }}>
                <li>Cryptographic SHA-256 hash of extracted pharmaceutical text</li>
                <li>Normalized International Nonproprietary Name (INN) matches and PubChem CIDs</li>
                <li>Processing latency metrics and OCR confidence index calculations</li>
                <li>Verification timestamp and regulatory pharmacopeial citation references</li>
              </ul>
            </section>

            {/* Section 6: Authoritative Database Grounding */}
            <section id="pharmacological-registries" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                6. Third-Party Pharmacological Reference Grounding
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Extracted active ingredients are grounded directly in authoritative public biomedical registries, including OpenFDA, the National Library of Medicine (NLM/PubChem), DailyMed (NIH), the WHO Essential Medicines List, and Indian Pharmacopoeia standards. MedLens transmits zero personal identifiers, browsing histories, or client tracking headers to these data providers during monograph queries.
              </p>
            </section>

            {/* Section 7: Transmission Security */}
            <section id="transmission-security" style={{ marginBottom: "32px", scrollMarginTop: "90px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                7. Transmission Security Standards (TLS 1.3)
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                All network interactions across MedLens web applications and API servers are strictly protected with Transport Layer Security (TLS 1.3) using high-grade cipher suites. End-to-end encryption ensures that scans, ingredient tokens, and report payloads remain completely confidential in transit.
              </p>
            </section>

            {/* Section 8: Inquiries */}
            <section id="governance">
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                8. Governance Inquiries &amp; Technical Audit Requests
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                For data governance inquiries, security disclosures, or compliance auditing regarding MedLens privacy protocols, direct inquiries to our technical team at <span style={{ fontFamily: "var(--font-mono)", color: "var(--blue)" }}>privacy@medlens.health</span>.
              </p>
            </section>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
