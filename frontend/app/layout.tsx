import type { Metadata, Viewport } from "next";
import "./globals.css";
import { LenisProvider } from "@/components/LenisProvider";
import { AuthProvider } from "@/context/AuthContext";
import PwaManager from "@/components/PwaManager";

export const viewport: Viewport = {
  themeColor: "#2563EB",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export const metadata: Metadata = {
  title: "MedLens: Pharmaceutical Packaging Verification and Composition Intelligence",
  description:
    "Clinical medicine composition analyzer. Inspect medicine blister packs, verify active chemical salts, and check ingredient equivalence against authoritative pharmacopeias.",
  keywords: ["medicine analyzer", "drug composition", "pharmaceutical salt verification", "RxNorm", "pharmacopeia", "PWA"],
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "MedLens",
  },
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512x512.png", sizes: "512x512", type: "image/png" },
      { url: "/favicon.ico" },
    ],
    shortcut: "/icon.svg",
    apple: [
      { url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    title: "MedLens: Pharmaceutical Packaging Verification",
    description: "Verify active pharmaceutical salts, calculate dosage equivalence, and inspect ingredient compositions directly from physical medicine packaging.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-[100dvh] antialiased">
        <AuthProvider>
          <LenisProvider>
            {children}
            <PwaManager />
          </LenisProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
