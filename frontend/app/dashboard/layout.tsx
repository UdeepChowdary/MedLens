"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { IcoScan } from "@/components/Icons";
import { Logo } from "@/components/Logo";
import { useAuth } from "@/context/AuthContext";

// Minimal icons for the sidebar
const IcoDashboard = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="9" rx="1" />
    <rect x="14" y="3" width="7" height="5" rx="1" />
    <rect x="14" y="12" width="7" height="9" rx="1" />
    <rect x="3" y="16" width="7" height="5" rx="1" />
  </svg>
);

const IcoHistory = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const IcoProfile = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const IcoLogout = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

const IcoCompare = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" y1="6" x2="21" y2="6"></line>
    <line x1="8" y1="12" x2="21" y2="12"></line>
    <line x1="8" y1="18" x2="21" y2="18"></line>
    <line x1="3" y1="6" x2="3.01" y2="6"></line>
    <line x1="3" y1="12" x2="3.01" y2="12"></line>
    <line x1="3" y1="18" x2="3.01" y2="18"></line>
  </svg>
);

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const isStandaloneMode =
        window.matchMedia("(display-mode: standalone)").matches ||
        (window.navigator as unknown as { standalone?: boolean }).standalone === true;
      setIsStandalone(isStandaloneMode);

      const handler = (e: any) => {
        e.preventDefault();
        setDeferredPrompt(e);
      };
      window.addEventListener("beforeinstallprompt", handler);
      return () => window.removeEventListener("beforeinstallprompt", handler);
    }
  }, []);

  const handleTriggerInstall = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === "accepted") {
        setDeferredPrompt(null);
      }
    } else {
      alert("To install MedLens on mobile:\n• iOS Safari: Tap Share (📤) and choose 'Add to Home Screen' (➕).\n• Android Chrome: Tap menu (⋮) and choose 'Install App' or 'Add to Home Screen'.");
    }
  };

  useEffect(() => {
    if (!loading && !user) {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [loading, user, router, pathname]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const navItems = [
    { name: "Overview", href: "/dashboard", icon: IcoDashboard },
    { name: "Scan New", href: "/dashboard/scan", icon: IcoScan },
    { name: "History", href: "/dashboard/history", icon: IcoHistory },
    { name: "Compare by Disease", href: "/dashboard/compare", icon: IcoCompare },
    { name: "Profile", href: "/dashboard/profile", icon: IcoProfile },
  ];

  if (loading || !user) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "var(--surface)",
          gap: "16px",
        }}
      >
        <Logo />
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            color: "var(--text-secondary)",
            fontSize: "14px",
          }}
        >
          <div
            style={{
              width: "18px",
              height: "18px",
              border: "2px solid #cbd5e1",
              borderTopColor: "var(--blue)",
              borderRadius: "50%",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <span>Verifying authentication...</span>
        </div>
        <style jsx>{`
          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "var(--surface)" }}>
      {/* Sidebar - Desktop */}
      <aside style={{
        width: "260px",
        backgroundColor: "white",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        top: 0,
        height: "100vh",
      }} className="desktop-only">
        <div style={{ padding: "24px 32px", borderBottom: "1px solid var(--border)" }}>
          <Logo href="/dashboard" />
        </div>
        
        <nav style={{ flex: 1, padding: "24px 16px", display: "flex", flexDirection: "column", gap: "8px" }}>
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link key={item.name} href={item.href} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  backgroundColor: isActive ? "var(--blue-dim)" : "transparent",
                  color: isActive ? "var(--blue)" : "var(--text-secondary)",
                  fontWeight: isActive ? 600 : 500,
                  transition: "all 0.2s"
                }} className="hover:bg-slate-50">
                  <item.icon size={20} color={isActive ? "var(--blue)" : "var(--text-secondary)"} />
                  <span>{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div style={{ padding: "20px 16px", borderTop: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "12px" }}>
          {/* PWA Install Button */}
          {!isStandalone && (
            <button
              type="button"
              onClick={handleTriggerInstall}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "8px 12px",
                borderRadius: "8px",
                backgroundColor: "#eff6ff",
                border: "1px solid #bfdbfe",
                color: "#2563eb",
                fontSize: "12.5px",
                fontWeight: 600,
                cursor: "pointer",
                width: "100%",
                textAlign: "left",
                transition: "all 0.15s ease",
              }}
              className="hover:bg-blue-100/70"
            >
              <span style={{ fontSize: "15px" }}>📱</span>
              <span>Install Mobile App</span>
            </button>
          )}

          {/* User Profile Mini Card */}
          <Link href="/dashboard/profile" style={{ textDecoration: "none" }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "8px 10px",
              borderRadius: "8px",
              backgroundColor: "var(--surface)",
              cursor: "pointer",
            }} className="hover:bg-slate-100 transition-colors">
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                backgroundColor: "var(--blue)",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 600,
                fontSize: "14px",
                overflow: "hidden",
                flexShrink: 0,
              }}>
                {user?.photoURL ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={user.photoURL} alt="Avatar" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                ) : (
                  (user?.displayName?.[0] || user?.email?.[0] || "U").toUpperCase()
                )}
              </div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user?.displayName || (user?.email ? user.email.split("@")[0] : "User")}
                </div>
                <div style={{ fontSize: "11px", color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user?.email || "Active User"}
                </div>
              </div>
            </div>
          </Link>

          <button
            onClick={handleLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "10px 12px",
              borderRadius: "8px",
              color: "var(--text-secondary)",
              fontWeight: 500,
              cursor: "pointer",
              border: "none",
              backgroundColor: "transparent",
              width: "100%",
              fontSize: "14px",
              textAlign: "left",
            }}
            className="hover:bg-slate-50 transition-colors"
          >
            <IcoLogout size={18} />
            <span>Log out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {/* Mobile Header */}
        <header style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 24px",
          backgroundColor: "white",
          borderBottom: "1px solid var(--border)",
          position: "sticky",
          top: 0,
          zIndex: 40
        }} className="mobile-only">
          <Logo href="/dashboard" />
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            style={{ background: "none", border: "none", cursor: "pointer", padding: "8px" }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </header>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <div style={{
            position: "absolute",
            top: "65px",
            left: 0,
            right: 0,
            backgroundColor: "white",
            borderBottom: "1px solid var(--border)",
            zIndex: 30,
            boxShadow: "var(--shadow-md)"
          }} className="mobile-only">
            <nav style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "8px" }}>
              {navItems.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                return (
                  <Link 
                    key={item.name} 
                    href={item.href} 
                    style={{ textDecoration: "none" }}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "12px",
                      padding: "12px 16px",
                      borderRadius: "8px",
                      backgroundColor: isActive ? "var(--blue-dim)" : "transparent",
                      color: isActive ? "var(--blue)" : "var(--text-secondary)",
                      fontWeight: isActive ? 600 : 500,
                    }}>
                      <item.icon size={20} color={isActive ? "var(--blue)" : "var(--text-secondary)"} />
                      <span>{item.name}</span>
                    </div>
                  </Link>
                );
              })}
              {!isStandalone && (
                <button
                  type="button"
                  onClick={() => {
                    setIsMobileMenuOpen(false);
                    handleTriggerInstall();
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    padding: "10px 16px",
                    borderRadius: "8px",
                    backgroundColor: "#eff6ff",
                    border: "1px solid #bfdbfe",
                    color: "#2563eb",
                    fontWeight: 600,
                    width: "100%",
                    textAlign: "left",
                    fontSize: "14px",
                    cursor: "pointer",
                  }}
                >
                  <span style={{ fontSize: "16px" }}>📱</span>
                  <span>Install MedLens App</span>
                </button>
              )}

              <button
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  handleLogout();
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  color: "var(--text-secondary)",
                  fontWeight: 500,
                  border: "none",
                  backgroundColor: "transparent",
                  width: "100%",
                  textAlign: "left",
                  fontSize: "15px",
                }}
              >
                <IcoLogout size={20} />
                <span>Log out</span>
              </button>
            </nav>
          </div>
        )}

        {/* Page Content */}
        <main style={{ flex: 1, overflowY: "auto", overflowX: "hidden" }}>
          {children}
        </main>
      </div>
    </div>
  );
}
