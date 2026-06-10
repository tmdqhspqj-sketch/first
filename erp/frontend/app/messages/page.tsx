"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, attachmentUrl, getToken, MessageAttachment, User } from "@/lib/api";

type Msg = {
  id: number;
  type: string;
  subject: string;
  body: string;
  sender: User;
  created_at: string;
  read_at?: string;
  attachments: MessageAttachment[];
};

type PendingFile = {
  filename: string;
  content_type: string;
  data_base64: string;
  size_bytes: number;
};

const MAX_FILE_BYTES = 5 * 1024 * 1024;

function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("파일을 읽을 수 없습니다"));
    reader.readAsDataURL(file);
  });
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function AttachmentLink({ att }: { att: MessageAttachment }) {
  const token = getToken();
  const href = `${attachmentUrl(att.id)}${token ? `?token=${encodeURIComponent(token)}` : ""}`;
  const isImage = att.content_type.startsWith("image/");

  return (
    <div style={{ marginTop: "0.5rem" }}>
      <a href={href} target="_blank" rel="noreferrer" style={{ fontSize: "0.9rem" }}>
        📎 {att.filename} ({formatSize(att.size_bytes)})
      </a>
      {isImage && token && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={href}
          alt={att.filename}
          style={{ display: "block", maxWidth: 240, marginTop: "0.5rem", borderRadius: 8 }}
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />
      )}
    </div>
  );
}

export default function MessagesPage() {
  const [inbox, setInbox] = useState<Msg[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [tab, setTab] = useState<"inbox" | "send">("inbox");
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [error, setError] = useState("");

  const load = () => api<Msg[]>("/messages/inbox").then(setInbox);

  useEffect(() => {
    load();
    api<User[]>("/users").then(setUsers);
  }, []);

  async function onFilesSelected(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    const files = Array.from(e.target.files ?? []);
    if (pendingFiles.length + files.length > 5) {
      setError("첨부파일은 최대 5개까지 가능합니다");
      e.target.value = "";
      return;
    }
    const next: PendingFile[] = [];
    for (const file of files) {
      if (file.size > MAX_FILE_BYTES) {
        setError(`${file.name}: 5MB 이하만 가능합니다`);
        continue;
      }
      const data_base64 = await readFileAsBase64(file);
      next.push({
        filename: file.name,
        content_type: file.type || "application/octet-stream",
        data_base64,
        size_bytes: file.size,
      });
    }
    setPendingFiles((prev) => [...prev, ...next]);
    e.target.value = "";
  }

  async function send(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const fd = new FormData(e.currentTarget);
    const type = fd.get("type") as string;
    const recipientIds =
      type === "note"
        ? [Number(fd.get("recipient"))]
        : String(fd.get("recipients"))
            .split(",")
            .map((s) => Number(s.trim()))
            .filter(Boolean);
    try {
      await api("/messages", {
        method: "POST",
        body: JSON.stringify({
          type,
          recipient_ids: recipientIds,
          subject: fd.get("subject"),
          body: fd.get("body"),
          attachments: pendingFiles.map(({ filename, content_type, data_base64 }) => ({
            filename,
            content_type,
            data_base64,
          })),
        }),
      });
      setPendingFiles([]);
      setTab("inbox");
      load();
      e.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "전송 실패");
    }
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
      {error && <p className="error">{error}</p>}

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
          <label className="label">첨부파일 (사진·문서, 최대 5개·각 5MB)</label>
          <input type="file" className="field" multiple accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip" onChange={onFilesSelected} />
          {pendingFiles.length > 0 && (
            <ul style={{ margin: "0.5rem 0", paddingLeft: "1.2rem", fontSize: "0.9rem" }}>
              {pendingFiles.map((f, i) => (
                <li key={`${f.filename}-${i}`}>
                  {f.filename} ({formatSize(f.size_bytes)}){" "}
                  <button type="button" className="btn btn-ghost" style={{ padding: "0 0.4rem" }} onClick={() => setPendingFiles((p) => p.filter((_, j) => j !== i))}>
                    삭제
                  </button>
                </li>
              ))}
            </ul>
          )}
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
                from {m.sender.rank?.name} {m.sender.name} · {new Date(m.created_at).toLocaleString("ko")}
                {!m.read_at && " · NEW"}
              </div>
              <p>{m.body}</p>
              {m.attachments?.map((att) => (
                <AttachmentLink key={att.id} att={att} />
              ))}
            </div>
          ))}
          {inbox.length === 0 && <p>받은 메시지가 없습니다.</p>}
        </div>
      )}
    </AppShell>
  );
}
