import React from "react";
import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Footer } from "@/components/Footer";

export const metadata = {
  title: "Privacy Policy | MedLens Clinical Data Governance",
  description: "MedLens data handling standards, zero-PII architecture, and ephemeral processing policies for medicine packaging inspection.",
};

export default function PrivacyPage() {
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
                Data Architecture & Compliance
              </div>
              <h1 style={{ fontSize: "32px", fontWeight: 800, color: "#0F172A", letterSpacing: "-0.02em", marginBottom: "12px" }}>
                Privacy Policy
              </h1>
              <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
                Effective Date: October 12, 2026 | Document ID: ML-SEC-POL-04
              </p>
            </div>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                1. Fundamental Operating Principle: Ephemeral Processing
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens operates as an informational pharmaceutical composition verification engine. We adhere to a strict ephemeral processing architecture: physical medicine packaging photos submitted for optical character recognition and salt normalization are held strictly in temporary volatile memory (RAM).
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Uploaded images are immediately discarded upon completion of the feature extraction pipeline. We do not store, catalog, train on, or persist raw image pixels to persistent disk, object storage buckets, or external third-party repositories.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                2. Zero-PII Policy and Packaging Boundary
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                MedLens is engineered exclusively to parse printed medicine blister strips, boxes, bottles, and formulation inserts. Our processing software does not collect Protected Health Information (PHI) or Personally Identifiable Information (PII).
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                In the event that an uploaded image inadvertently contains human faces, patient names, prescription receipts, or hospital admission cards, automated detection routines apply black bounding redaction masks across those regions prior to tokenization, ensuring non-medicinal attributes are never indexed.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                3. Immutable Audit Telemetry
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75, marginBottom: "12px" }}>
                To support deterministic safety verification, system auditing, and model accuracy benchmarks, our infrastructure generates a non-reversible cryptographic SHA-256 digest of verified packaging tokens.
              </p>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                The persistent audit log contains solely:
              </p>
              <ul style={{ paddingLeft: "24px", marginTop: "8px", color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.75 }}>
                <li>Cryptographic hash of extracted pharmaceutical text</li>
                <li>Normalized International Nonproprietary Name (INN) matching scores</li>
                <li>Execution latency metrics and confidence index calculations</li>
                <li>Timestamp of verification event</li>
              </ul>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                4. Third-Party Pharmacological Reference Grounding
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                Extracted active ingredients are cross-referenced directly against public, authoritative biomedical registries, including OpenFDA, the National Library of Medicine (NLM/PubChem), DailyMed, and the World Health Organization (WHO) Essential Medicines List. We do not transmit user telemetry, IP tracking markers, or personal identifiers to these clinical data providers during reference verification queries.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                5. Client Session Data and Local Storage
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                When you perform a scan in your browser, image previews may be stored in your browser session storage exclusively to display your immediate verification results. This data is isolated to your local device sandbox and is cleared automatically upon browser session termination. We do not deploy third-party advertising tracking cookies or biometric fingerprinters.
              </p>
            </section>

            <section style={{ marginBottom: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                6. Transmission Security Standards
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                All network communication with MedLens endpoints utilizes Transport Layer Security (TLS 1.3) with modern cipher suites. In-transit packet encryption ensures that image payloads and extracted report data cannot be intercepted or modified by intermediary nodes.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#0F172A", marginBottom: "12px" }}>
                7. Governance Inquiries and Contact
              </h2>
              <p style={{ fontSize: "14.5px", color: "var(--text-secondary)", lineHeight: 1.75 }}>
                For technical auditing requests, data integrity questions, or administrative security notices regarding MedLens data protocols, direct formal inquiries to our technical governance office at <span style={{ fontFamily: "var(--font-mono)", color: "var(--blue)" }}>governance@medlens.internal</span>.
              </p>
            </section>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
