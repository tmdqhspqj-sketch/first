"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

type Admin = {
  id: number;
  login_id: string;
  name: string;
  active: boolean;
  deactivated_at: string | null;
  created_at: string;
};

export default function AdminsPage() {
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [error, setError] = useState("");

  const load = () => api<Admin[]>("/admins").then(setAdmins).catch((e) => setError(String(e)));

  useEffect(() => {
    load();
  }, []);

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await api("/admins", {
        method: "POST",
        body: JSON.stringify({
          login_id: fd.get("login_id"),
          password: fd.get("password"),
          name: fd.get("name"),
        }),
      });
      load();
      e.currentTarget.reset();
    } catch (err) {
      setError(String(err));
    }
  }

  async function deactivate(id: number) {
    if (!confirm("이 관리자를 비활성화할까요? 7일 후 자동 삭제됩니다.")) return;
    await api(`/admins/${id}/deactivate`, { method: "POST" });
    load();
  }

  async function activate(id: number) {
    await api(`/admins/${id}/activate`, { method: "POST" });
    load();
  }

  return (
    <AppShell>
      <h1>관리자 계정</h1>
      <p style={{ color: "var(--muted)" }}>
        비활성화된 계정은 7일 후 자동 삭제됩니다. 마지막 활성 관리자는 비활성화할 수 없습니다.
      </p>
      {error && <p className="error">{error}</p>}
      <form className="card" onSubmit={create}>
        <label className="label">로그인 ID</label>
        <input name="login_id" className="field" required />
        <label className="label">비밀번호</label>
        <input name="password" type="password" className="field" required />
        <label className="label">이름</label>
        <input name="name" className="field" required />
        <button type="submit" className="btn btn-primary">
          관리자 추가
        </button>
      </form>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>이름</th>
              <th>상태</th>
              <th>비활성화일</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {admins.map((a) => (
              <tr key={a.id}>
                <td>{a.login_id}</td>
                <td>{a.name}</td>
                <td>{a.active ? "활성" : "비활성"}</td>
                <td>{a.deactivated_at ? new Date(a.deactivated_at).toLocaleString("ko-KR") : "-"}</td>
                <td>
                  {a.active ? (
                    <button type="button" className="btn btn-ghost" onClick={() => deactivate(a.id)}>
                      비활성화
                    </button>
                  ) : (
                    <button type="button" className="btn btn-ghost" onClick={() => activate(a.id)}>
                      복구
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
