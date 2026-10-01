import type { Metadata } from "next";
import { Outfit, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { LenisProvider } from "@/components/LenisProvider";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
  weight: ["400", "500", "600", "700", "800", "900"],
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "MedLens — Scan. Understand. Verify.",
  description:
    "MedLens is an AI-powered medicine composition analyzer. Upload a photo of any medicine label and get a clear, verified breakdown of every ingredient — active, inactive, and their purposes.",
  keywords: ["medicine analyzer", "drug composition", "ingredient verification", "OCR medicine", "pharmacy tool"],
  openGraph: {
    title: "MedLens — Scan. Understand. Verify.",
    description: "Turn any medicine label into clear, verified, structured information — in seconds.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${outfit.variable} ${plusJakarta.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-[100dvh] antialiased">
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}

