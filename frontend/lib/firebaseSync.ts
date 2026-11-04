import { doc, getDoc, setDoc } from "firebase/firestore";
import { db } from "./firebase";

export interface UserHealthProfile {
  allergies: string[];
  conditions: string[];
  updatedAt?: string;
}

/**
 * Saves health profile to Cloud Firestore under users/{uid}/profile.
 * Gracefully falls back if Firestore is offline or uninitialized.
 */
export async function saveProfileToFirestore(
  uid: string,
  profile: UserHealthProfile
): Promise<boolean> {
  if (!db || !uid) return false;
  try {
    const userDocRef = doc(db, "users", uid);
    await setDoc(
      userDocRef,
      {
        profile: {
          allergies: profile.allergies,
          conditions: profile.conditions,
          updatedAt: new Date().toISOString(),
        },
      },
      { merge: true }
    );
    return true;
  } catch (err) {
    console.warn("Firestore profile sync notice (non-fatal):", err);
    return false;
  }
}

/**
 * Loads health profile from Cloud Firestore and syncs to localStorage.
 */
export async function loadProfileFromFirestore(
  uid: string
): Promise<UserHealthProfile | null> {
  if (!db || !uid) return null;
  try {
    const userDocRef = doc(db, "users", uid);
    const snap = await getDoc(userDocRef);
    if (snap.exists()) {
      const data = snap.data();
      if (data?.profile) {
        const profile: UserHealthProfile = {
          allergies: Array.isArray(data.profile.allergies) ? data.profile.allergies : [],
          conditions: Array.isArray(data.profile.conditions) ? data.profile.conditions : [],
          updatedAt: data.profile.updatedAt,
        };
        // Sync to local device cache
        try {
          localStorage.setItem("medlens_user_allergies", JSON.stringify(profile.allergies));
          localStorage.setItem("medlens_user_conditions", JSON.stringify(profile.conditions));
        } catch {
          // Ignore local storage error
        }
        return profile;
      }
    }
    return null;
  } catch (err) {
    console.warn("Firestore profile fetch notice (non-fatal):", err);
    return null;
  }
}
