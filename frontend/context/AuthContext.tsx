"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import {
  User,
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { auth, googleProvider, isFirebaseConfigured } from "@/lib/firebase";

export interface MedLensUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  isAnonymous?: boolean;
}

interface AuthContextType {
  user: MedLensUser | null;
  loading: boolean;
  isFirebaseReady: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithEmail: (email: string, pass: string) => Promise<void>;
  signUpWithEmail: (email: string, pass: string) => Promise<void>;
  logout: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  isFirebaseReady: false,
  signInWithGoogle: async () => {},
  signInWithEmail: async () => {},
  signUpWithEmail: async () => {},
  logout: async () => {},
  getIdToken: async () => null,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<MedLensUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isFirebaseConfigured && auth) {
      const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: User | null) => {
        if (firebaseUser) {
          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            displayName: firebaseUser.displayName || (firebaseUser.email ? firebaseUser.email.split("@")[0] : "Researcher"),
            photoURL: firebaseUser.photoURL,
            isAnonymous: firebaseUser.isAnonymous,
          });
          // Cache session token for immediate synchronous header availability
          try {
            const token = await firebaseUser.getIdToken();
            localStorage.setItem("medlens_auth_token", token);
            localStorage.setItem("medlens_session_id", firebaseUser.uid);
          } catch {
            // Ignore token storage errors
          }
        } else {
          setUser(null);
          localStorage.removeItem("medlens_auth_token");
        }
        setLoading(false);
      });

      return () => unsubscribe();
    } else {
      // Local development fallback session if Firebase keys are not yet populated
      const localUser = localStorage.getItem("medlens_local_user");
      if (localUser) {
        try {
          setUser(JSON.parse(localUser));
        } catch {
          setUser(null);
        }
      }
      setLoading(false);
    }
  }, []);

  const signInWithGoogle = async () => {
    if (isFirebaseConfigured && auth && googleProvider) {
      await signInWithPopup(auth, googleProvider);
    } else {
      // Dev mode local mock user
      const mockUser: MedLensUser = {
        uid: "usr_google_dev_demo",
        email: "demo.researcher@medlens.health",
        displayName: "Dr. Demo Researcher",
        photoURL: null,
      };
      setUser(mockUser);
      localStorage.setItem("medlens_local_user", JSON.stringify(mockUser));
      localStorage.setItem("medlens_session_id", mockUser.uid);
    }
  };

  const signInWithEmail = async (email: string, pass: string) => {
    if (isFirebaseConfigured && auth) {
      await signInWithEmailAndPassword(auth, email, pass);
    } else {
      const mockUser: MedLensUser = {
        uid: `usr_${email.replace(/[^a-zA-Z0-9]/g, "_")}`,
        email,
        displayName: email.split("@")[0],
        photoURL: null,
      };
      setUser(mockUser);
      localStorage.setItem("medlens_local_user", JSON.stringify(mockUser));
      localStorage.setItem("medlens_session_id", mockUser.uid);
    }
  };

  const signUpWithEmail = async (email: string, pass: string) => {
    if (isFirebaseConfigured && auth) {
      await createUserWithEmailAndPassword(auth, email, pass);
    } else {
      await signInWithEmail(email, pass);
    }
  };

  const logout = async () => {
    if (isFirebaseConfigured && auth) {
      await signOut(auth);
    }
    setUser(null);
    localStorage.removeItem("medlens_local_user");
    localStorage.removeItem("medlens_auth_token");
    localStorage.removeItem("medlens_session_id");
  };

  const getIdToken = async (): Promise<string | null> => {
    if (isFirebaseConfigured && auth?.currentUser) {
      return auth.currentUser.getIdToken();
    }
    return localStorage.getItem("medlens_auth_token") || localStorage.getItem("medlens_session_id");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isFirebaseReady: isFirebaseConfigured,
        signInWithGoogle,
        signInWithEmail,
        signUpWithEmail,
        logout,
        getIdToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
