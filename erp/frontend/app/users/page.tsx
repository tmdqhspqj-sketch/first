"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, User } from "@/lib/api";

type Rank = { id: number; name: string; level: number };

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [ranks, setRanks] = useState<Rank[]>([]);

  const load = () => api<User[]>("/users").then(setUsers);

  useEffect(() => {
    load();
    api<Rank[]>("/users/ranks").then(setRanks);
  }, []);

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    await api("/users", {
      method: "POST",
      body: JSON.stringify({
        login_id: fd.get("login_id"),
        password: fd.get("password"),
        name: fd.get("name"),
        rank_id: Number(fd.get("rank_id")),
      }),
    });
    load();
    e.currentTarget.reset();
  }

  return (
    <AppShell>
      <h1>사용자 관리</h1>
      <p style={{ color: "var(--muted)" }}>manager는 본인보다 낮은 직급만 생성할 수 있습니다.</p>
      <form className="card" onSubmit={create}>
        <label className="label">로그인 ID</label>
        <input name="login_id" className="field" required />
        <label className="label">비밀번호</label>
        <input name="password" type="password" className="field" required />
        <label className="label">이름</label>
        <input name="name" className="field" required />
        <label className="label">직급</label>
        <select name="rank_id" className="field">
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
