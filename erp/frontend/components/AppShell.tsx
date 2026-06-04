"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, clearToken, User } from "@/lib/api";

const links = [
  { href: "/dashboard", label: "대시보드" },
  { href: "/approvals", label: "결재" },
  { href: "/rooms", label: "회의실" },
  { href: "/messages", label: "메시지" },
  { href: "/users", label: "사용자" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<User | null>(null);

  useEffect(() => {
    api<User>("/auth/me")
      .then(setMe)
      .catch(() => router.replace("/login"));
  }, [router]);

  if (!me) return <p style={{ padding: "2rem" }}>로딩…</p>;

  const showUsers = me.role === "super" || me.role === "manager";

  return (
    <div className="layout">
      <aside className="sidebar">
        <strong style={{ display: "block", marginBottom: "1rem" }}>Hong ERP</strong>
        <p style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: "1rem" }}>
          {me.name} · {me.rank.name}
          {me.rank.name === "부장" && " (팀장)"}
          <br />
          <span className="badge">{me.role}</span>
        </p>
        {links
          .filter((l) => l.href !== "/users" || showUsers)
          .map((l) => (
            <Link key={l.href} href={l.href} className={path === l.href ? "active" : ""}>
              {l.label}
            </Link>
          ))}
        <button
          type="button"
          className="btn btn-ghost"
          style={{ marginTop: "1.5rem", width: "100%", color: "#cbd5e1" }}
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
        >
          로그아웃
        </button>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
