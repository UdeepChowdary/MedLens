"use client";

import React, { useState, useRef } from "react";
import { IcoScan } from "../Icons";
import LiveCamera from "./LiveCamera";

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
}

export default function UploadZone({ onFileSelected }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    if (!showCamera) {
      fileInputRef.current?.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  if (showCamera) {
    return (
      <div style={{ width: "100%", padding: "24px 0" }}>
        <LiveCamera 
          onCapture={(file) => {
            setShowCamera(false);
            onFileSelected(file);
          }}
          onClose={() => setShowCamera(false)}
        />
      </div>
    );
  }

  return (
    <div
      className="relative w-full max-w-2xl mx-auto rounded-2xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer"
      style={{ 
        minHeight: "350px", 
        backgroundColor: isDragging ? 'rgba(37, 99, 235, 0.05)' : 'var(--surface-light)',
        borderColor: isDragging ? 'var(--blue)' : '#cbd5e1',
        transition: 'all 0.3s ease',
        transform: isDragging ? 'scale(1.02)' : 'scale(1)',
        padding: "48px"
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/jpg, image/webp"
        className="hidden"
      />
      
      <div style={{ backgroundColor: "rgba(37, 99, 235, 0.1)", padding: "20px", borderRadius: "50%", marginBottom: "24px" }}>
        <IcoScan size={40} color="var(--blue)" />
      </div>
      
      <h3 style={{ fontSize: "24px", fontWeight: "bold", color: "var(--text-primary)", marginBottom: "12px", textAlign: "center" }}>
        Upload or Take a Photo
      </h3>
      <p style={{ color: "var(--text-secondary)", textAlign: "center", maxWidth: "450px", marginBottom: "32px", fontSize: "15px" }}>
        Drag and drop an image of your medicine blister pack, bottle, or label, or click to browse.
      </p>
      
      <div style={{ display: "flex", gap: "14px", flexWrap: "wrap", justifyContent: "center" }}>
        <button 
          onClick={handleClick}
          className="btn-primary"
        >
          Select Image
        </button>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setShowCamera(true);
          }}
          className="btn-secondary"
        >
          Use Camera
        </button>
      </div>
      
      <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "32px" }}>
        Supports .jpg, .png, .webp up to 15MB
      </p>
    </div>
  );
}
