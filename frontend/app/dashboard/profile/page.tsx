"use client";

import React from "react";

export default function ProfilePage() {
  return (
    <div style={{ padding: "32px", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Health Profile
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Manage your personal information, allergies, and account settings.
      </p>

      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        padding: "32px",
        marginBottom: "24px"
      }}>
        <h2 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "24px", color: "var(--text-primary)" }}>
          Personal Information
        </h2>
        
        <div style={{ display: "grid", gap: "20px" }}>
          <div>
            <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
              Full Name
            </label>
            <input 
              type="text" 
              defaultValue="Udeep Chowdary"
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", fontSize: "15px"
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
              Email Address
            </label>
            <input 
              type="email" 
              defaultValue="udeep@example.com"
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", fontSize: "15px"
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ 
        backgroundColor: "white", 
        border: "1px solid var(--border)", 
        borderRadius: "16px", 
        padding: "32px"
      }}>
        <h2 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "16px", color: "var(--text-primary)" }}>
          Known Allergies & Conditions
        </h2>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "24px" }}>
          This information is used to warn you if a scanned medicine contains contraindicating ingredients.
        </p>
        
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "24px" }}>
          {["Penicillin", "Ibuprofen"].map((allergy) => (
            <div key={allergy} style={{ 
              backgroundColor: "var(--red-dim)", 
              color: "var(--red)", 
              padding: "6px 12px", 
              borderRadius: "6px",
              fontSize: "14px",
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}>
              {allergy}
              <button style={{ background: "none", border: "none", color: "var(--red)", cursor: "pointer", display: "flex" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          ))}
          <button style={{ 
            backgroundColor: "transparent", 
            border: "1px dashed var(--border)", 
            color: "var(--text-secondary)", 
            padding: "6px 12px", 
            borderRadius: "6px",
            fontSize: "14px",
            fontWeight: 500,
            cursor: "pointer"
          }}>
            + Add Allergy
          </button>
        </div>
        
        <button className="btn-primary">
          Save Changes
        </button>
      </div>
    </div>
  );
}
