import React, { useState } from "react";

export const FAQSection = () => {
  const [open, setOpen] = useState<number | null>(0);
  const faqs = [
    {
      cat: "Clinical Safety",
      q: "Is MedLens a diagnostic tool?",
      a: "No. MedLens is strictly an educational and informational platform. It analyzes medicine packaging text and provides ingredient breakdowns. It never advises taking a medication, adjusting dosages, or diagnosing conditions. Always consult a licensed healthcare professional.",
    },
    {
      cat: "Verification Technology",
      q: "How does MedLens prevent AI hallucinations in medicine data?",
      a: "MedLens uses a deterministic verification pipeline: the LLM is never a medical knowledge source — only a plain-language synthesis formatter (temperature=0.0). Any ingredient or dosage claim in the output that was not verified in the OCR text and reference database is strictly purged. Output schemas are enforced via strict validation.",
    },
    {
      cat: "Privacy & Data",
      q: "Is my uploaded packaging photo stored?",
      a: "No. Images are processed in ephemeral volatile server RAM and discarded immediately after feature extraction. Only a cryptographic SHA-256 hash and extracted text tokens are stored for audit — raw patient or packaging pixels are never persisted.",
    },
    {
      cat: "Verification Technology",
      q: "What sources does MedLens use for verification?",
      a: "MedLens cross-references authoritative sources including OpenFDA, PubChem / National Library of Medicine (NLM), WHO Essential Medicines, and DailyMed. All claims cite their source registry for complete transparency.",
    },
    {
      cat: "Bioequivalence",
      q: "Can MedLens compare two different medicine brands?",
      a: "Yes. The Brand Comparison Engine scans two medicines, normalizes both to their canonical active International Nonproprietary Names (INNs), and highlights active salt equivalence, dosage parity, and excipient differences side by side.",
    },
    {
      cat: "Image Processing",
      q: "What happens if a medicine label is blurry or low quality?",
      a: "The image preprocessing pipeline runs a Laplacian variance blur check. If the image clarity score falls below the threshold (σ² < 100), MedLens rejects the photo and asks you to retake it rather than risk an unreliable OCR extraction.",
    },
  ];

  return (
    <section id="faqs" style={{ padding: "80px 0", background: "#ffffff", borderTop: "1px solid var(--border)" }}>
      <div className="container" style={{ maxWidth: 768 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <span className="section-label" style={{ marginBottom: 10, display: "block" }}>FAQ</span>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.02em", color: "#0F172A" }}>
            Questions, honestly answered
          </h2>
          <p style={{ fontFamily: "var(--font-body)", fontSize: 15.5, color: "var(--text-secondary)", marginTop: 8 }}>
            Everything you need to know about how MedLens works, what it doesn&apos;t do, and how your data is handled.
          </p>
        </div>

        {faqs.map((faq, i) => (
          <div key={i} className="faq-item">
            <button
              className="faq-btn"
              onClick={() => setOpen(open === i ? null : i)}
              aria-expanded={open === i}
              aria-controls={`faq-answer-${i}`}
              id={`faq-question-${i}`}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700, color: "var(--blue)", background: "var(--blue-dim)", padding: "2px 6px", borderRadius: 4 }}>
                  {faq.cat}
                </span>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 15.5, fontWeight: 700, color: "#0F172A" }}>
                  {faq.q}
                </span>
              </div>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  flexShrink: 0,
                  background: open === i ? "var(--blue)" : "var(--surface-alt)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s",
                  transform: open === i ? "rotate(45deg)" : "none",
                }}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={open === i ? "#fff" : "#475569"} strokeWidth="2.5" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </div>
            </button>
            {/* Smooth animated accordion using CSS grid-template-rows */}
            <div
              className={`faq-body${open === i ? " open" : ""}`}
              id={`faq-answer-${i}`}
              role="region"
              aria-labelledby={`faq-question-${i}`}
            >
              <div className="faq-body-inner">
                <div style={{ paddingBottom: 20 }}>
                  <p style={{ fontFamily: "var(--font-body)", fontSize: 14.5, color: "var(--text-secondary)", lineHeight: 1.75 }}>
                    {faq.a}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
