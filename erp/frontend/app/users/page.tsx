"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, User } from "@/lib/api";

type Rank = { id: number; name: string; level: number };

const EMPTY = { login_id: "", password: "", name: "", rank_id: 0 };

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [ranks, setRanks] = useState<Rank[]>([]);
  const [form, setForm] = useState(EMPTY);
  const [formKey, setFormKey] = useState(0);
  const [error, setError] = useState("");

  const load = () => api<User[]>("/users").then(setUsers);

  useEffect(() => {
    load();
    api<Rank[]>("/users/ranks").then((r) => {
      setRanks(r);
      if (r.length) setForm((f) => ({ ...f, rank_id: r[0].id }));
    });
  }, []);

  function resetForm(rankId: number) {
    setForm({ login_id: "", password: "", name: "", rank_id: rankId });
    setFormKey((k) => k + 1);
  }

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/users", {
        method: "POST",
        body: JSON.stringify(form),
      });
      load();
      resetForm(ranks[0]?.id ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "추가 실패");
    }
  }

  return (
    <AppShell>
      <h1>사용자 관리</h1>
      <p style={{ color: "var(--muted)" }}>manager는 본인보다 낮은 직급만 생성할 수 있습니다.</p>
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
        <label className="label">직급</label>
        <select
          className="field"
          value={form.rank_id}
          onChange={(e) => setForm((f) => ({ ...f, rank_id: Number(e.target.value) }))}
        >
          {ranks.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>
        <button type="submit" className="btn btn-primary">
          사용자 추가
        </button>
      </form>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>이름</th>
              <th>직급</th>
              <th>역할</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.login_id}</td>
                <td>{u.name}</td>
                <td>
                  {u.rank.name}
                  {u.rank.name === "부장" && " (팀장)"}
                </td>
                <td>{u.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
