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

const EMPTY = { login_id: "", password: "", name: "" };

export default function AdminsPage() {
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [form, setForm] = useState(EMPTY);
  const [formKey, setFormKey] = useState(0);
  const [error, setError] = useState("");

  const load = () => api<Admin[]>("/admins").then(setAdmins).catch((e) => setError(String(e)));

  useEffect(() => {
    load();
  }, []);

  function resetForm() {
    setForm(EMPTY);
    setFormKey((k) => k + 1);
  }

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/admins", {
        method: "POST",
        body: JSON.stringify(form),
      });
      load();
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : "추가 실패");
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
      <form key={formKey} className="card" onSubmit={create}>
        <label className="label">로그인 ID</label>
        <input
          className="field"
          required
          value={form.login_id}
          onChange={(e) => setForm((f) => ({ ...f, login_id: e.target.value }))}
        />
        <label className="label">비밀번호</label>
        <input
          className="field"
          type="password"
          required
          value={form.password}
          onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
        />
        <label className="label">이름</label>
        <input
          className="field"
          required
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
        />
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
