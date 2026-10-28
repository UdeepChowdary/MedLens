"use client";

import React, { useState, useEffect } from "react";
import { IcoShield } from "@/components/Icons";

const DEFAULT_ALLERGIES = ["Penicillin", "Ibuprofen"];

export default function ProfilePage() {
  const [fullName, setFullName] = useState("Udeep Chowdary");
  const [email, setEmail] = useState("udeep@example.com");
  const [allergies, setAllergies] = useState<string[]>(DEFAULT_ALLERGIES);
  const [newAllergyInput, setNewAllergyInput] = useState("");
  const [isAddingAllergy, setIsAddingAllergy] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("medlens_user_allergies");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setAllergies(parsed);
        }
      }
      const storedName = localStorage.getItem("medlens_user_name");
      if (storedName) setFullName(storedName);
      const storedEmail = localStorage.getItem("medlens_user_email");
      if (storedEmail) setEmail(storedEmail);
    } catch {
      // Fallback to defaults
    }
  }, []);

  const handleRemoveAllergy = (allergyToRemove: string) => {
    setAllergies((prev) => prev.filter((a) => a !== allergyToRemove));
  };

  const handleAddAllergy = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = newAllergyInput.trim();
    if (trimmed && !allergies.some((a) => a.toLowerCase() === trimmed.toLowerCase())) {
      setAllergies((prev) => [...prev, trimmed]);
      setNewAllergyInput("");
      setIsAddingAllergy(false);
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem("medlens_user_allergies", JSON.stringify(allergies));
      localStorage.setItem("medlens_user_name", fullName);
      localStorage.setItem("medlens_user_email", email);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch {
      // Ignore storage errors
    }
  };

  return (
    <div style={{ padding: "32px", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
        Health Profile & Allergies
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "32px" }}>
        Manage your profile and documented drug allergies. MedLens actively cross-checks every packaging scan against this list to safeguard you from adverse drug reactions.
      </p>

      {saveSuccess && (
        <div style={{
          marginBottom: "24px",
          padding: "16px 20px",
          backgroundColor: "var(--surface-green, #ecfdf5)",
          borderLeft: "4px solid var(--green, #10b981)",
          borderRadius: "8px",
          color: "var(--green, #059669)",
          fontWeight: 500,
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}>
          <IcoShield size={20} color="var(--green)" />
          <span>Profile and allergy settings saved successfully! Future medicine scans will cross-reference these entries.</span>
        </div>
      )}

      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "32px",
        marginBottom: "24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
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
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", fontSize: "15px", outline: "none"
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%", padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--border)", fontSize: "15px", outline: "none"
              }}
            />
          </div>
        </div>
      </div>

      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "32px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <h2 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "8px", color: "var(--text-primary)" }}>
          Documented Drug Allergies & Contraindicated Salts
        </h2>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "24px", lineHeight: "1.5" }}>
          Add chemical names or drug classes you are allergic to (e.g. <em>Penicillin, Paracetamol, Aspirin, Ibuprofen, Sulfa, Lactose</em>).
        </p>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginBottom: "28px" }}>
          {allergies.map((allergy) => (
            <div key={allergy} style={{
              backgroundColor: "var(--red-dim, #fee2e2)",
              color: "var(--red, #dc2626)",
              padding: "8px 14px",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              gap: "8px",
              border: "1px solid rgba(239,68,68,0.2)"
            }}>
              <span>{allergy}</span>
              <button
                type="button"
                onClick={() => handleRemoveAllergy(allergy)}
                style={{ background: "none", border: "none", color: "var(--red, #dc2626)", cursor: "pointer", display: "flex", padding: "2px" }}
                title={`Remove ${allergy}`}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          ))}

          {isAddingAllergy ? (
            <form onSubmit={handleAddAllergy} style={{ display: "flex", gap: "6px", alignItems: "center" }}>
              <input
                type="text"
                autoFocus
                placeholder="e.g. Paracetamol"
                value={newAllergyInput}
                onChange={(e) => setNewAllergyInput(e.target.value)}
                style={{
                  padding: "7px 12px",
                  borderRadius: "6px",
                  border: "1px solid var(--blue)",
                  fontSize: "14px",
                  outline: "none"
                }}
              />
              <button
                type="submit"
                style={{
                  backgroundColor: "var(--blue)",
                  color: "white",
                  border: "none",
                  padding: "8px 14px",
                  borderRadius: "6px",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer"
                }}
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setIsAddingAllergy(false)}
                style={{
                  backgroundColor: "transparent",
                  color: "var(--text-secondary)",
                  border: "1px solid var(--border)",
                  padding: "7px 10px",
                  borderRadius: "6px",
                  fontSize: "13px",
                  cursor: "pointer"
                }}
              >
                Cancel
              </button>
            </form>
          ) : (
            <button
              type="button"
              onClick={() => setIsAddingAllergy(true)}
              style={{
                backgroundColor: "transparent",
                border: "1px dashed var(--border)",
                color: "var(--blue)",
                padding: "8px 16px",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px"
              }}
            >
              <span>+ Add Allergy</span>
            </button>
          )}
        </div>

        <button
          onClick={handleSave}
          style={{
            backgroundColor: "var(--blue)",
            color: "white",
            padding: "12px 24px",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "15px",
            border: "none",
            cursor: "pointer",
            boxShadow: "0 2px 4px rgba(37,99,235,0.2)"
          }}
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}
