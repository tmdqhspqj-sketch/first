"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [loginId, setLoginId] = useState("hongseungbo");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ login_id: loginId, password }),
      });
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인 실패");
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "4rem auto", padding: "0 1rem" }}>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>Hong ERP 로그인</h1>
        <form onSubmit={submit}>
          <label className="label">ID</label>
          <input className="field" value={loginId} onChange={(e) => setLoginId(e.target.value)} />
          <label className="label">비밀번호</label>
          <input
            className="field"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
            로그인
          </button>
        </form>
        <p style={{ fontSize: "0.8rem", color: "var(--muted)", marginTop: "1rem" }}>
          관리자: admin / admin 또는 hongseungbo / hongsb · 데모: bujang 등 비밀번호 demo1
        </p>
      </div>
    </div>
  );
}
