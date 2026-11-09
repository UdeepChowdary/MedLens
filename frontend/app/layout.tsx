import type { Metadata, Viewport } from "next";
import "./globals.css";
import { LenisProvider } from "@/components/LenisProvider";
import { AuthProvider } from "@/context/AuthContext";
import { AccessibilityProvider } from "@/context/AccessibilityContext";
import PwaManager from "@/components/PwaManager";
import AccessibilityToolbar from "@/components/AccessibilityToolbar";

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
  keywords: ["medicine analyzer", "drug composition", "pharmaceutical salt verification", "RxNorm", "pharmacopeia", "PWA", "accessibility"],
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
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only"
          style={{
            position: "fixed",
            top: 12,
            left: 12,
            backgroundColor: "#2563eb",
            color: "#ffffff",
            padding: "10px 18px",
            borderRadius: 8,
            fontWeight: 700,
            fontSize: "14px",
            zIndex: 10000,
            textDecoration: "none",
            boxShadow: "0 4px 14px rgba(37,99,235,0.4)",
          }}
        >
          Skip to main content
        </a>
        <AuthProvider>
          <AccessibilityProvider>
            <LenisProvider>
              {children}
              <PwaManager />
              <AccessibilityToolbar />
            </LenisProvider>
          </AccessibilityProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
