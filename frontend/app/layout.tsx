import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { LenisProvider } from "@/components/LenisProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "MedLens: Pharmaceutical Packaging Verification and Composition Intelligence",
  description:
    "Clinical medicine composition analyzer. Inspect medicine blister packs, verify active chemical salts, and check ingredient equivalence against authoritative pharmacopeias.",
  keywords: ["medicine analyzer", "drug composition", "pharmaceutical salt verification", "RxNorm", "pharmacopeia"],
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico" }
    ],
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
  openGraph: {
    title: "MedLens: Pharmaceutical Packaging Verification",
    description: "Verify active pharmaceutical salts, calculate dosage equivalence, and inspect ingredient compositions directly from physical medicine packaging.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body className="min-h-[100dvh] antialiased">
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}

