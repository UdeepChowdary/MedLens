# 🔬 MedLens Frontend

This directory contains the user interface and client-side verification engine for **MedLens**, built with [Next.js 16](https://nextjs.org/) (Turbopack, App Router), [React 19](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), and [Tailwind CSS](https://tailwindcss.com/).

> For complete project documentation, system architecture diagrams, and medical verification pipeline specs, please refer to the [Root README](../README.md).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Production Build
```bash
npm run build
npm run start
```

---

## 📁 Frontend File Hierarchy

- `app/page.tsx` — Complete interactive MedLens UI, live verification engine, prescription inspection cards, and safety breakdown.
- `app/layout.tsx` — App root layout, font optimization, and SEO metadata.
- `app/globals.css` — Modern glassmorphic theme tokens, animations, and custom scrollbar styling.
- `public/` — Optimized assets and demonstration images for testing the verification engine.
- `next.config.ts` — Next.js configuration.
- `tailwind.config.ts` / PostCSS — Design styling pipeline.
