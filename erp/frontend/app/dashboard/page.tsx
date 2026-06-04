"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, Approval, User } from "@/lib/api";

export default function DashboardPage() {
  const [me, setMe] = useState<User | null>(null);
  const [inbox, setInbox] = useState<Approval[]>([]);
  const [all, setAll] = useState<Approval[]>([]);

  useEffect(() => {
    api<User>("/auth/me").then(setMe);
    api<Approval[]>("/approvals/inbox").then(setInbox).catch(() => setInbox([]));
    api<Approval[]>("/approvals").then(setAll).catch(() => setAll([]));
  }, []);

  const pending = all.filter((a) => a.status.startsWith("pending")).length;

  return (
    <AppShell>
      <h1>대시보드</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: "1rem" }}>
        <div className="card">
          <div className="label">내 승인 대기</div>
          <strong style={{ fontSize: "1.75rem" }}>{inbox.length}</strong>
        </div>
        <div className="card">
          <div className="label">진행 중 결재</div>
          <strong style={{ fontSize: "1.75rem" }}>{pending}</strong>
        </div>
        <div className="card">
          <div className="label">역할</div>
          <strong>{me?.role ?? "…"}</strong>
          {me?.role === "super" && (
            <p style={{ fontSize: "0.85rem", color: "var(--muted)", margin: "0.5rem 0 0" }}>
              결재 승인 없음 · 전체 관람만
            </p>
          )}
        </div>
      </div>
      <div className="card">
        <h3 style={{ marginTop: 0 }}>결재선</h3>
        <p>팀장(부장) → 상무 → 사장</p>
      </div>
    </AppShell>
  );
}
