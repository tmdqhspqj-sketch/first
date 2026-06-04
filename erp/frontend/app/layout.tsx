import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hong ERP",
  description: "간단 사내 ERP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
