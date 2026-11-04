"use client";

import React, { useState, useEffect } from "react";
import { IcoShield } from "@/components/Icons";
import { useAuth } from "@/context/AuthContext";
import { verifyGeminiKey, VerifyKeyResponse } from "@/lib/api";
import { saveProfileToFirestore, loadProfileFromFirestore } from "@/lib/firebaseSync";

const DEFAULT_ALLERGIES = ["Penicillin", "Ibuprofen"];
const DEFAULT_CONDITIONS = ["GERD / Acid Reflux"];

const SUGGESTED_ALLERGIES = ["Penicillin", "Sulfa drugs", "Aspirin", "Ibuprofen", "Lactose", "Paracetamol", "NSAIDs"];
const SUGGESTED_CONDITIONS = [
  "GERD / Acid Reflux",
  "Hypertension",
  "Diabetes Type 2",
  "Asthma",
  "Chronic Kidney Disease",
  "Osteoporosis",
  "Peptic Ulcer",
  "Liver Impairment",
  "Pregnancy",
];

export default function ProfilePage() {
  const { user } = useAuth();
  const [fullName, setFullName] = useState(user?.displayName || "User");
  const [email, setEmail] = useState(user?.email || "user@medlens.health");

  // Health Profile State
  const [allergies, setAllergies] = useState<string[]>(DEFAULT_ALLERGIES);
  const [newAllergyInput, setNewAllergyInput] = useState("");
  const [isAddingAllergy, setIsAddingAllergy] = useState(false);

  const [conditions, setConditions] = useState<string[]>(DEFAULT_CONDITIONS);
  const [newConditionInput, setNewConditionInput] = useState("");
  const [isAddingCondition, setIsAddingCondition] = useState(false);

  // BYOK Gemini API Key State (Optional)
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [isTestingKey, setIsTestingKey] = useState(false);
  const [keyValidation, setKeyValidation] = useState<VerifyKeyResponse | null>(null);

  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (user?.displayName) setFullName(user.displayName);
    if (user?.email) setEmail(user.email);
    if (user?.uid) {
      loadProfileFromFirestore(user.uid).then((cloudProfile) => {
        if (cloudProfile) {
          if (cloudProfile.allergies?.length) setAllergies(cloudProfile.allergies);
          if (cloudProfile.conditions?.length) setConditions(cloudProfile.conditions);
        }
      });
    }
  }, [user]);

  useEffect(() => {
    try {
      const storedAllergies = localStorage.getItem("medlens_user_allergies");
      if (storedAllergies) {
        const parsed = JSON.parse(storedAllergies);
        if (Array.isArray(parsed)) setAllergies(parsed);
      }

      const storedConditions = localStorage.getItem("medlens_user_conditions");
      if (storedConditions) {
        const parsed = JSON.parse(storedConditions);
        if (Array.isArray(parsed)) setConditions(parsed);
      }

      const storedKey = localStorage.getItem("medlens_gemini_api_key");
      if (storedKey) setGeminiApiKey(storedKey);

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

  const handleAddAllergy = (itemToAdd?: string) => {
    const val = (itemToAdd || newAllergyInput).trim();
    if (val && !allergies.some((a) => a.toLowerCase() === val.toLowerCase())) {
      setAllergies((prev) => [...prev, val]);
      setNewAllergyInput("");
      setIsAddingAllergy(false);
    }
  };

  const handleRemoveCondition = (condToRemove: string) => {
    setConditions((prev) => prev.filter((c) => c !== condToRemove));
  };

  const handleAddCondition = (itemToAdd?: string) => {
    const val = (itemToAdd || newConditionInput).trim();
    if (val && !conditions.some((c) => c.toLowerCase() === val.toLowerCase())) {
      setConditions((prev) => [...prev, val]);
      setNewConditionInput("");
      setIsAddingCondition(false);
    }
  };

  const handleTestGeminiKey = async () => {
    if (!geminiApiKey.trim()) {
      setKeyValidation({ valid: false, message: "Please enter a Gemini API key first." });
      return;
    }
    setIsTestingKey(true);
    setKeyValidation(null);
    try {
      const { data, error } = await verifyGeminiKey(geminiApiKey.trim());
      if (error) {
        setKeyValidation({ valid: false, message: error.message });
      } else if (data) {
        setKeyValidation(data);
      }
    } catch {
      setKeyValidation({ valid: false, message: "Connection to verification service failed." });
    } finally {
      setIsTestingKey(false);
    }
  };

  const handleSave = async () => {
    try {
      localStorage.setItem("medlens_user_allergies", JSON.stringify(allergies));
      localStorage.setItem("medlens_user_conditions", JSON.stringify(conditions));
      if (geminiApiKey.trim()) {
        localStorage.setItem("medlens_gemini_api_key", geminiApiKey.trim());
      } else {
        localStorage.removeItem("medlens_gemini_api_key");
      }
      localStorage.setItem("medlens_user_name", fullName);
      localStorage.setItem("medlens_user_email", email);

      // Synchronize with Cloud Firestore if user is authenticated
      if (user?.uid) {
        await saveProfileToFirestore(user.uid, { allergies, conditions });
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch {
      // Ignore storage errors
    }
  };

  return (
    <div style={{ padding: "32px", maxWidth: "840px", margin: "0 auto" }}>
      <div style={{ marginBottom: "28px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "8px" }}>
          Personalized Health Profile & Safety Settings
        </h1>
        <p style={{ color: "var(--text-secondary)", lineHeight: "1.6" }}>
          Tailor MedLens to your health profile. Scanned medications are actively cross-checked against your documented
          allergies and pre-existing conditions. Optionally provide your Gemini API key for clinical AI-powered cross-reactivity intelligence.
        </p>
      </div>

      {saveSuccess && (
        <div style={{
          marginBottom: "24px",
          padding: "16px 20px",
          backgroundColor: "#ecfdf5",
          borderLeft: "4px solid #10b981",
          borderRadius: "8px",
          color: "#059669",
          fontWeight: 500,
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}>
          <IcoShield size={20} color="#10b981" />
          <span>Profile and health conditions saved &amp; synced across devices! Future medicine scans will cross-reference these entries.</span>
        </div>
      )}

      {/* Personal Info */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <h2 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "20px", color: "var(--text-primary)" }}>
          Personal Information
        </h2>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
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

      {/* Documented Allergies */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-primary)" }}>
            Documented Drug Allergies & Chemical Sensitivities
          </h2>
          <span style={{ fontSize: "12px", padding: "3px 8px", borderRadius: "12px", backgroundColor: "#fee2e2", color: "#dc2626", fontWeight: 600 }}>
            {allergies.length} Documented
          </span>
        </div>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "20px", lineHeight: "1.5" }}>
          Add substances or drug classes that trigger adverse reactions (e.g. <em>Penicillin, Sulfa, Ibuprofen, Aspirin, Lactose</em>).
        </p>

        {/* Existing Allergy Tags */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginBottom: "16px" }}>
          {allergies.map((allergy) => (
            <div key={allergy} style={{
              backgroundColor: "#fee2e2",
              color: "#dc2626",
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
                style={{ background: "none", border: "none", color: "#dc2626", cursor: "pointer", display: "flex", padding: "2px" }}
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
            <form onSubmit={(e) => { e.preventDefault(); handleAddAllergy(); }} style={{ display: "flex", gap: "6px", alignItems: "center" }}>
              <input
                type="text"
                autoFocus
                placeholder="e.g. Sulfa drugs"
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

        {/* Quick Suggestion Chips */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", fontSize: "12px", color: "var(--text-secondary)" }}>
          <span>Suggestions:</span>
          {SUGGESTED_ALLERGIES.filter((s) => !allergies.some((a) => a.toLowerCase() === s.toLowerCase())).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => handleAddAllergy(item)}
              style={{
                padding: "3px 8px",
                borderRadius: "12px",
                border: "1px solid var(--border)",
                backgroundColor: "#f8fafc",
                color: "var(--text-secondary)",
                cursor: "pointer",
                fontSize: "12px"
              }}
            >
              + {item}
            </button>
          ))}
        </div>
      </div>

      {/* Pre-Existing Health Conditions & Diseases */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-primary)" }}>
            Pre-Existing Health Conditions & Chronic Diseases
          </h2>
          <span style={{ fontSize: "12px", padding: "3px 8px", borderRadius: "12px", backgroundColor: "#e0f2fe", color: "#0284c7", fontWeight: 600 }}>
            {conditions.length} Documented
          </span>
        </div>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "20px", lineHeight: "1.5" }}>
          Document diagnosed medical conditions to evaluate whether a medication is clinically indicated, requires dosage adjustment, or is contraindicated.
        </p>

        {/* Existing Condition Tags */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginBottom: "16px" }}>
          {conditions.map((cond) => (
            <div key={cond} style={{
              backgroundColor: "#e0f2fe",
              color: "#0369a1",
              padding: "8px 14px",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              gap: "8px",
              border: "1px solid rgba(2,132,199,0.2)"
            }}>
              <span>{cond}</span>
              <button
                type="button"
                onClick={() => handleRemoveCondition(cond)}
                style={{ background: "none", border: "none", color: "#0369a1", cursor: "pointer", display: "flex", padding: "2px" }}
                title={`Remove ${cond}`}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          ))}

          {isAddingCondition ? (
            <form onSubmit={(e) => { e.preventDefault(); handleAddCondition(); }} style={{ display: "flex", gap: "6px", alignItems: "center" }}>
              <input
                type="text"
                autoFocus
                placeholder="e.g. Hypertension"
                value={newConditionInput}
                onChange={(e) => setNewConditionInput(e.target.value)}
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
                onClick={() => setIsAddingCondition(false)}
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
              onClick={() => setIsAddingCondition(true)}
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
              <span>+ Add Condition</span>
            </button>
          )}
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", fontSize: "12px", color: "var(--text-secondary)" }}>
          <span>Suggestions:</span>
          {SUGGESTED_CONDITIONS.filter((s) => !conditions.some((c) => c.toLowerCase() === s.toLowerCase())).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => handleAddCondition(item)}
              style={{
                padding: "3px 8px",
                borderRadius: "12px",
                border: "1px solid var(--border)",
                backgroundColor: "#f8fafc",
                color: "var(--text-secondary)",
                cursor: "pointer",
                fontSize: "12px"
              }}
            >
              + {item}
            </button>
          ))}
        </div>
      </div>

      {/* Bring Your Own Key (BYOK) - Google Gemini API */}
      <div style={{
        backgroundColor: "white",
        border: "1px solid #e2e8f0",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "32px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-primary)" }}>
                Google Gemini API Key
              </h2>
              <span style={{
                fontSize: "12px",
                padding: "3px 10px",
                borderRadius: "12px",
                backgroundColor: "#f1f5f9",
                color: "#475569",
                fontWeight: 600,
                border: "1px solid #cbd5e1"
              }}>
                Optional • Bring Your Own Key (BYOK)
              </span>
            </div>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
              Provide your own Google Gemini API key to unlock clinical AI cross-reactivity and contraindication assessments tailored directly to your health conditions and allergies. If omitted, MedLens operates on standard pharmacopeia monograph rules.
            </p>
          </div>
        </div>

        <div style={{ marginTop: "20px" }}>
          <label style={{ display: "block", fontSize: "14px", fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>
            Gemini API Key
          </label>
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <div style={{ position: "relative", flex: 1 }}>
              <input
                type={showApiKey ? "text" : "password"}
                placeholder="AIzaSy..."
                value={geminiApiKey}
                onChange={(e) => {
                  setGeminiApiKey(e.target.value);
                  setKeyValidation(null);
                }}
                style={{
                  width: "100%",
                  padding: "12px 48px 12px 16px",
                  borderRadius: "8px",
                  border: "1px solid var(--border)",
                  fontSize: "14px",
                  fontFamily: "monospace",
                  outline: "none"
                }}
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                style={{
                  position: "absolute",
                  right: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "var(--text-secondary)",
                  fontSize: "12px",
                  fontWeight: 600
                }}
              >
                {showApiKey ? "Hide" : "Show"}
              </button>
            </div>

            <button
              type="button"
              onClick={handleTestGeminiKey}
              disabled={isTestingKey || !geminiApiKey.trim()}
              style={{
                backgroundColor: "#f8fafc",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
                padding: "12px 20px",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 600,
                cursor: isTestingKey || !geminiApiKey.trim() ? "not-allowed" : "pointer",
                opacity: !geminiApiKey.trim() ? 0.6 : 1,
                whiteSpace: "nowrap"
              }}
            >
              {isTestingKey ? "Testing..." : "Test Key"}
            </button>
          </div>

          {/* Validation Feedback */}
          {keyValidation && (
            <div style={{
              marginTop: "12px",
              padding: "10px 14px",
              borderRadius: "8px",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              backgroundColor: keyValidation.valid ? "#ecfdf5" : "#fef2f2",
              color: keyValidation.valid ? "#059669" : "#dc2626",
              border: `1px solid ${keyValidation.valid ? "#a7f3d0" : "#fecaca"}`
            }}>
              <span>{keyValidation.valid ? "✓" : "⚠"}</span>
              <span>{keyValidation.message}</span>
            </div>
          )}

          <div style={{ marginTop: "12px", fontSize: "12px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
            <span>Your key is stored securely in your browser and sent only when running personalized consultations.</span>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noreferrer"
              style={{ color: "var(--blue)", textDecoration: "none", fontWeight: 600 }}
            >
              Get free Gemini API Key ↗
            </a>
          </div>
        </div>
      </div>

      {/* Global Save Button */}
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button
          onClick={handleSave}
          style={{
            backgroundColor: "var(--blue)",
            color: "white",
            padding: "14px 32px",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "16px",
            border: "none",
            cursor: "pointer",
            boxShadow: "0 2px 4px rgba(37,99,235,0.2)"
          }}
        >
          Save All Changes
        </button>
      </div>
    </div>
  );
}
