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
    <html lang="en" className={`${inter.variable}`}>
      <body className="min-h-[100dvh] antialiased">
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}

