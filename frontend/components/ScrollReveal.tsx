"use client";

import React from "react";

interface ScrollRevealProps {
  children: React.ReactNode;
  variant?: "fade-up" | "fade-in" | "fade-left" | "fade-right" | "scale-in";
  delay?: number;
  duration?: number;
  threshold?: number;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Standard Viewport Container
 * Provides clean, instant content presentation without disorienting translation or scale animations.
 */
export function ScrollReveal({
  children,
  className,
  style,
}: ScrollRevealProps) {
  return (
    <div className={className || ""} style={style}>
      {children}
    </div>
  );
}
