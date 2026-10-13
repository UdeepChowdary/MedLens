"use client";

import React from "react";
import Link from "next/link";
import { IcoScan, IcoArrow } from "@/components/Icons";

export default function DashboardOverviewPage() {
  return (
    <div style={{ padding: "32px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Welcome back, Udeep
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Here&apos;s an overview of your recent scans and activity.
      </p>

      {/* Quick Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px", marginBottom: "40px" }}>
        <Link href="/dashboard/scan" style={{ textDecoration: "none" }}>
          <div style={{
            backgroundColor: "var(--blue)",
            borderRadius: "16px",
            padding: "24px",
            color: "white",
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
            gap: "16px",
            boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.3)",
            transition: "transform 0.2s"
          }} className="hover:-translate-y-1">
            <div style={{ backgroundColor: "rgba(255, 255, 255, 0.2)", padding: "12px", borderRadius: "12px" }}>
              <IcoScan size={28} color="white" />
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "4px" }}>Scan New Medicine</h3>
              <p style={{ fontSize: "14px", opacity: 0.9 }}>Identify ingredients and verify safety instantly.</p>
            </div>
          </div>
        </Link>

        <div style={{
          backgroundColor: "white",
          border: "1px solid var(--border)",
          borderRadius: "16px",
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          gap: "16px",
          boxShadow: "var(--shadow-sm)"
        }}>
          <div style={{ backgroundColor: "var(--surface-alt)", padding: "12px", borderRadius: "12px" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
              <path d="M9 14h6"></path>
              <path d="M9 18h6"></path>
              <path d="M9 10h.01"></path>
            </svg>
          </div>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>Health Profile</h3>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>Update allergies and current medications.</p>
          </div>
        </div>
      </div>

      {/* Activity Analytics Chart */}
      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        padding: "24px", 
        marginBottom: "40px",
        boxShadow: "var(--shadow-sm)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
          <h2 style={{ fontSize: "18px", fontWeight: "bold", color: "var(--text-primary)", margin: 0 }}>
            Activity Overview
          </h2>
          <span style={{ fontSize: "13px", fontWeight: 500, color: "var(--blue)", backgroundColor: "var(--surface-blue)", padding: "4px 12px", borderRadius: "6px" }}>
            This Week
          </span>
        </div>
        
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", height: "160px", paddingBottom: "16px", borderBottom: "1px dashed var(--border)", gap: "8px" }}>
          {[
            { day: "Mon", value: 30, active: false },
            { day: "Tue", value: 50, active: false },
            { day: "Wed", value: 20, active: false },
            { day: "Thu", value: 80, active: false },
            { day: "Fri", value: 100, active: true },
            { day: "Sat", value: 40, active: false },
            { day: "Sun", value: 60, active: false },
          ].map((bar, i) => (
            <div key={i} className="group" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px", flex: 1 }}>
              <div style={{ 
                width: "100%", 
                maxWidth: "40px", 
                height: `${bar.value}%`, 
                backgroundColor: bar.active ? "var(--blue)" : "var(--surface-blue)", 
                borderRadius: "6px",
                transition: "all 0.3s ease",
                cursor: "pointer"
              }} className="hover:opacity-80" title={`${bar.value}% activity`} />
              <span style={{ fontSize: "12px", color: bar.active ? "var(--blue)" : "var(--text-muted)", fontWeight: bar.active ? 600 : 500 }}>
                {bar.day}
              </span>
            </div>
          ))}
        </div>
        
        <div style={{ display: "flex", justifyContent: "space-between", paddingTop: "16px" }}>
          <div>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: "0 0 4px 0" }}>Total Scans</p>
            <p style={{ fontSize: "20px", fontWeight: "bold", color: "var(--text-primary)", margin: 0 }}>12</p>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: "0 0 4px 0" }}>Safety Alerts</p>
            <p style={{ fontSize: "20px", fontWeight: "bold", color: "var(--amber)", margin: 0 }}>2</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <h2 style={{ fontSize: "20px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "16px" }}>
        Recent Scans
      </h2>
      
      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        overflow: "hidden" 
      }}>
        {[
          { id: "test-123", name: "Dolo 650", date: "Today, 9:42 AM", status: "Verified", color: "var(--green)" },
          { id: "test-124", name: "Allegra 120mg", date: "Yesterday", status: "Warning", color: "var(--amber)" },
          { id: "test-125", name: "Unknown Supplement", date: "Oct 2, 2026", status: "Unknown", color: "var(--text-muted)" }
        ].map((item, i) => (
          <Link key={i} href={`/dashboard/results/${item.id}`} style={{ textDecoration: "none" }}>
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "space-between", 
              padding: "16px 24px",
              borderBottom: i !== 2 ? "1px solid var(--border)" : "none",
              transition: "background-color 0.2s"
            }} className="hover:bg-slate-50">
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <div style={{ 
                  width: "48px", 
                  height: "48px", 
                  backgroundColor: "var(--surface-blue)", 
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <IcoScan size={20} color="var(--blue)" />
                </div>
                <div>
                  <h4 style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "15px" }}>{item.name}</h4>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{item.date}</p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <span style={{ 
                  fontSize: "12px", 
                  fontWeight: 600, 
                  color: item.color, 
                  backgroundColor: `${item.color}15`, 
                  padding: "4px 10px", 
                  borderRadius: "4px" 
                }}>
                  {item.status}
                </span>
                <IcoArrow size={18} color="var(--text-muted)" />
              </div>
            </div>
          </Link>
        ))}
      </div>
      
      <div style={{ textAlign: "center", marginTop: "16px" }}>
        <Link href="/dashboard/history" style={{ 
          fontSize: "14px", 
          fontWeight: 600, 
          color: "var(--blue)", 
          textDecoration: "none" 
        }}>
          View full history →
        </Link>
      </div>
    </div>
  );
}
