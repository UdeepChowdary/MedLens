"use client";

import { useEffect, useRef } from "react";

interface ScrollRevealProps {
  children: React.ReactNode;
  /**
   * Animation variant to apply on entry.
   * "fade-up"   — translate Y 32px → 0, opacity 0 → 1  (default)
   * "fade-in"   — opacity 0 → 1, no translate
   * "fade-left" — translate X -32px → 0, opacity 0 → 1
   * "fade-right"— translate X 32px → 0, opacity 0 → 1
   * "scale-in"  — scale 0.94 → 1, opacity 0 → 1
   */
  variant?: "fade-up" | "fade-in" | "fade-left" | "fade-right" | "scale-in";
  /** Delay in milliseconds before the animation plays. Use for staggering. */
  delay?: number;
  /** Duration in milliseconds. Default 600ms. */
  duration?: number;
  /** IntersectionObserver threshold (0–1). Default 0.12. */
  threshold?: number;
  /** Additional className forwarded to the wrapper div. */
  className?: string;
  style?: React.CSSProperties;
}

const INITIAL_STYLES: Record<ScrollRevealProps["variant"] & string, string> = {
  "fade-up":    "opacity:0; transform:translateY(32px)",
  "fade-in":    "opacity:0",
  "fade-left":  "opacity:0; transform:translateX(-32px)",
  "fade-right": "opacity:0; transform:translateX(32px)",
  "scale-in":   "opacity:0; transform:scale(0.94)",
};

/**
 * ScrollReveal — Zero-dependency scroll-triggered animation wrapper.
 *
 * Uses IntersectionObserver to add a `.revealed` class when the element
 * enters the viewport. CSS transitions (defined in globals.css) handle
 * the actual animation — no GSAP, no framer-motion weight.
 *
 * Works with Lenis smooth scroll out of the box.
 */
export function ScrollReveal({
  children,
  variant = "fade-up",
  delay = 0,
  duration = 620,
  threshold = 0.12,
  className,
  style,
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Respect prefers-reduced-motion — skip animation entirely
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) {
      el.style.opacity = "1";
      el.style.transform = "none";
      return;
    }

    // Apply initial hidden state via inline style
    const initStyle = INITIAL_STYLES[variant];
    initStyle.split(";").forEach((declaration) => {
      const [prop, value] = declaration.split(":").map((s) => s.trim());
      if (prop && value) {
        (el.style as unknown as Record<string, string>)[
          prop.replace(/-([a-z])/g, (_, c: string) => c.toUpperCase())
        ] = value;
      }
    });

    // Set transition
    el.style.transition = `opacity ${duration}ms cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms, transform ${duration}ms cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms`;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.style.opacity = "1";
          el.style.transform = "none";
          observer.disconnect();
        }
      },
      { threshold }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [variant, delay, duration, threshold]);

  return (
    <div ref={ref} className={className} style={style}>
      {children}
    </div>
  );
}
