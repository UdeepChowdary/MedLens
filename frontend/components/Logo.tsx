import Link from "next/link";
import Image from "next/image";

interface LogoProps {
  dark?: boolean;
  height?: number;
  href?: string | null;
}

export const Logo = ({ dark = false, height = 44, href = "/" }: LogoProps) => {
  const scaledHeight = height * 1.3;

  const content = (
    <Image 
      src={dark ? "/image.png" : "/logo.png"} 
      alt="MedLens Logo" 
      width={scaledHeight * 3.5} 
      height={scaledHeight} 
      style={{ height: `${scaledHeight}px`, width: "auto" }}
      priority
    />
  );

  if (href) {
    return (
      <Link href={href} style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
        {content}
      </Link>
    );
  }

  return (
    <span style={{ display: "inline-flex", alignItems: "center" }}>
      {content}
    </span>
  );
};
