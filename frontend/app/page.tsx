"use client";

import React, { useState, useEffect, useRef } from "react";

import { ScrollReveal } from "@/components/ScrollReveal";


import { Navbar } from "@/components/Navbar";
import { HeroSection } from "@/components/HeroSection";
import { ProblemSection } from "@/components/ProblemSection";
import { HowItWorksSection } from "@/components/HowItWorksSection";
import { WhyMedLensSection } from "@/components/WhyMedLensSection";
import { BrandComparisonSection } from "@/components/BrandComparisonSection";
import { FAQSection } from "@/components/FAQSection";
import { CTASection } from "@/components/CTASection";
import { Footer } from "@/components/Footer";

/* ============================================================
   MAIN PAGE EXPORT
   ============================================================ */
export default function HomePage() {
  return (
    <main>
      <Navbar />

      {/* Hero is above the fold — no reveal needed */}
      <HeroSection />

      <ScrollReveal variant="fade-up" delay={0}>
        <ProblemSection />
      </ScrollReveal>

      <ScrollReveal variant="fade-up" delay={0}>
        <HowItWorksSection />
      </ScrollReveal>

      <ScrollReveal variant="fade-up" delay={0}>
        <WhyMedLensSection />
      </ScrollReveal>

      <ScrollReveal variant="fade-up" delay={0}>
        <BrandComparisonSection />
      </ScrollReveal>

      <ScrollReveal variant="fade-up" delay={0}>
        <FAQSection />
      </ScrollReveal>

      <ScrollReveal variant="scale-in" delay={0} duration={700}>
        <CTASection />
      </ScrollReveal>

      <ScrollReveal variant="fade-in" delay={0} duration={500}>
        <Footer />
      </ScrollReveal>
    </main>
  );
}

