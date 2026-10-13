"use client";

import React from "react";

/**
 * Standard Layout Provider
 * Preserves clean, instantaneous native browser scrolling without floaty inertia or lag.
 */
export function LenisProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
