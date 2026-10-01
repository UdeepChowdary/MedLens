import React from "react";
import Image from "next/image";

export const Logo = ({ dark = false, height = 44 }: { dark?: boolean; height?: number }) => {
  const scaledHeight = height * 1.3;
  
  return (
    <a href="#" style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
      <Image 
        src="/logo.png" 
        alt="MedLens Logo" 
        width={scaledHeight * 3.5} 
        height={scaledHeight} 
        style={{ height: `${scaledHeight}px`, width: "auto" }}
        priority
      />
    </a>
  );
};
