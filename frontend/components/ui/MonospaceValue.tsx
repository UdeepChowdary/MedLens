import React from "react";

interface MonospaceValueProps {
  value: string | number;
  unit: string;
  className?: string;
}

export default function MonospaceValue({ value, unit, className = "" }: MonospaceValueProps) {
  return (
    <span className={`font-mono inline-flex items-baseline gap-1 ${className}`}>
      <span className="font-bold tracking-tight">{value}</span>
      <span className="text-sm opacity-80">{unit}</span>
    </span>
  );
}
