import React from "react";

export const Logo = ({ dark = false, height = 44 }: { dark?: boolean; height?: number }) => (
  <a href="#" style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
    {/* eslint-disable-next-line @next/next/no-img-element */}
    <img
      src="/e1697cba-8f8e-4d0b-95ac-bb247a4214be.png"
      alt="MedLens — Scan. Understand. Verify."
      style={{
        height,
        width: "auto",
        objectFit: "contain",
        display: "block",
        filter: dark ? "brightness(0) invert(1)" : "none",
      }}
    />
  </a>
);
