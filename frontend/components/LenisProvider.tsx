"use client";

import { ReactLenis } from "lenis/react";
import "lenis/dist/lenis.css";

/**
 * LenisProvider — Global smooth-scroll wrapper.
 *
 * Options:
 *  lerp      – Linear interpolation factor (0–1). Lower = slower, dreamier scroll.
 *              0.08 gives a "weighted" feel without being sluggish.
 *  duration  – Scroll animation duration in seconds (used when lerp is not set).
 *  smoothWheel – Enable inertia on mouse wheel (true by default in Lenis v2+).
 *
 * Wrap the root layout <body> children with this component.
 * Lenis automatically respects `prefers-reduced-motion` for accessibility.
 */
export function LenisProvider({ children }: { children: React.ReactNode }) {
  return (
    <ReactLenis
      root
      options={{
        lerp: 0.09,
        duration: 1.3,
        smoothWheel: true,
        // Prevent Lenis from intercepting hash-link anchor clicks — let the
        // browser handle #how-it-works, #faqs, etc. natively via Lenis's
        // built-in anchor support.
        anchors: true,
      }}
    >
      {children}
    </ReactLenis>
  );
}
