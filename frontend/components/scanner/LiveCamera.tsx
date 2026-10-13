"use client";

import React, { useRef, useState, useEffect } from "react";
import { IcoX } from "../Icons";

interface LiveCameraProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export default function LiveCamera({ onCapture, onClose }: LiveCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: "environment" } 
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error("Error accessing camera:", err);
        setError("Unable to access camera. Please check permissions.");
      }
    }

    startCamera();

    return () => {
      // Cleanup stream on unmount
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext("2d");
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to blob (File)
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "camera-scan.jpg", { type: "image/jpeg" });
            
            // Stop camera tracks before returning
            if (stream) {
              stream.getTracks().forEach(track => track.stop());
            }
            
            onCapture(file);
          }
        }, "image/jpeg", 0.9);
      }
    }
  };

  return (
    <div style={{
      width: "100%", 
      maxWidth: "600px", 
      margin: "0 auto", 
      backgroundColor: "white", 
      borderRadius: "16px", 
      overflow: "hidden", 
      border: "1px solid var(--border)",
      boxShadow: "var(--shadow-md)",
      position: "relative"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px", borderBottom: "1px solid var(--border)" }}>
        <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>Live Camera</h3>
        <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-secondary)" }}>
          <IcoX size={20} />
        </button>
      </div>

      <div style={{ position: "relative", backgroundColor: "black", width: "100%", height: "400px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {error ? (
          <p style={{ color: "white", padding: "24px", textAlign: "center" }}>{error}</p>
        ) : (
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
        <canvas ref={canvasRef} style={{ display: "none" }} />
        
        {/* Aiming Reticle */}
        {!error && (
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: "80%", height: "60%", border: "2px dashed rgba(255,255,255,0.5)", borderRadius: "8px", pointerEvents: "none" }}></div>
        )}
      </div>

      <div style={{ padding: "24px", display: "flex", justifyContent: "center", backgroundColor: "var(--surface)" }}>
        <button 
          onClick={handleCapture}
          disabled={!!error}
          style={{
            width: "64px",
            height: "64px",
            borderRadius: "50%",
            backgroundColor: "white",
            border: "4px solid var(--blue)",
            cursor: error ? "not-allowed" : "pointer",
            boxShadow: "0 4px 12px rgba(37, 99, 235, 0.2)",
            opacity: error ? 0.5 : 1
          }}
          aria-label="Capture photo"
        />
      </div>
    </div>
  );
}
