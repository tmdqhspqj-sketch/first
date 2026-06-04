"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, User } from "@/lib/api";

type Msg = {
  id: number;
  type: string;
  subject: string;
  body: string;
  sender: User;
  created_at: string;
  read_at?: string;
};

export default function MessagesPage() {
  const [inbox, setInbox] = useState<Msg[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [tab, setTab] = useState<"inbox" | "send">("inbox");

  const load = () => api<Msg[]>("/messages/inbox").then(setInbox);

  useEffect(() => {
    load();
    api<User[]>("/users").then(setUsers);
  }, []);

  async function send(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const type = fd.get("type") as string;
    const recipientIds =
      type === "note"
        ? [Number(fd.get("recipient"))]
        : String(fd.get("recipients"))
            .split(",")
            .map((s) => Number(s.trim()))
            .filter(Boolean);
    await api("/messages", {
      method: "POST",
      body: JSON.stringify({
        type,
        recipient_ids: recipientIds,
        subject: fd.get("subject"),
        body: fd.get("body"),
      }),
    });
    setTab("inbox");
    load();
  }

  return (
    <AppShell>
      <h1>메시지</h1>
      <button type="button" className="btn btn-ghost" onClick={() => setTab("inbox")}>
        받은함
      </button>{" "}
      <button type="button" className="btn btn-ghost" onClick={() => setTab("send")}>
        보내기
      </button>

      {tab === "send" && (
        <form className="card" onSubmit={send} style={{ marginTop: "1rem" }}>
          <label className="label">종류</label>
          <select name="type" className="field" defaultValue="note">
            <option value="note">쪽지 (1명)</option>
            <option value="mail">메일 (여러 명, 쉼표 구분 ID)</option>
          </select>
          <label className="label">받는 사람 (쪽지)</label>
          <select name="recipient" className="field">
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name} ({u.login_id})
              </option>
            ))}
          </select>
          <label className="label">받는 사람 ID들 (메일)</label>
          <input name="recipients" className="field" placeholder="예: 3,4" />
          <label className="label">제목</label>
          <input name="subject" className="field" />
          <label className="label">내용</label>
          <textarea name="body" className="field" rows={4} required />
          <button type="submit" className="btn btn-primary">
            전송
          </button>
        </form>
      )}

      {tab === "inbox" && (
        <div className="card" style={{ marginTop: "1rem" }}>
          {inbox.map((m) => (
            <div key={m.id} style={{ borderBottom: "1px solid var(--border)", padding: "0.75rem 0" }}>
              <strong>
                [{m.type === "note" ? "쪽지" : "메일"}] {m.subject || "(제목 없음)"}
              </strong>
              <div style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
                from {m.sender.name} · {new Date(m.created_at).toLocaleString("ko")}
                {!m.read_at && " · NEW"}
              </div>
              <p>{m.body}</p>
            </div>
          ))}
          {inbox.length === 0 && <p>받은 메시지가 없습니다.</p>}
        </div>
      )}
    </AppShell>
  );
}
