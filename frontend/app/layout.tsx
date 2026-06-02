import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "First Agent | 로컬 AI 에이전트",
  description: "Gemma 4 · Ollama · RAG · 비전 · 툴 — 로컬에서 동작하는 AI 에이전트",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
