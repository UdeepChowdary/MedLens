import React from "react";
import { IcoCheck, IcoX, IcoShield } from "../Icons";

interface BadgeProps {
  status: "verified" | "medium" | "unverified";
  label?: string;
  className?: string;
}

export default function Badge({ status, label, className = "" }: BadgeProps) {
  const config = {
    verified: {
      bg: "bg-emerald-100",
      text: "text-emerald-700",
      border: "border-emerald-200",
      icon: <IcoCheck size={12} color="#047857" />,
      defaultLabel: "High Confidence"
    },
    medium: {
      bg: "bg-cyan-100",
      text: "text-cyan-800",
      border: "border-cyan-200",
      icon: <IcoShield size={12} color="#155e75" />,
      defaultLabel: "Cross-Check Recommended"
    },
    unverified: {
      bg: "bg-amber-100",
      text: "text-amber-800",
      border: "border-amber-200",
      icon: <IcoX size={12} />, // IcoX defaults to red, but we might want an amber variant if possible, sticking to default for now
      defaultLabel: "Unverified Entity"
    }
  };

  const style = config[status];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${style.bg} ${style.text} ${style.border} ${className}`}>
      {style.icon}
      {label || style.defaultLabel}
    </span>
  );
}
