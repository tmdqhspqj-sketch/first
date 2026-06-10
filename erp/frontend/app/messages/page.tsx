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

type Recipient = {
  id: number;
  login_id: string;
  name: string;
  rank: { id: number; name: string; level: number };
};

type PendingFile = {
  filename: string;
  content_type: string;
  data_base64: string;
  size_bytes: number;
};

const MAX_FILE_BYTES = 5 * 1024 * 1024;
type SendForm = {
  type: "note" | "mail";
  subject: string;
  body: string;
  noteRecipientId: number;
  mailRecipientIds: number[];
};

const EMPTY_FORM: SendForm = { type: "note", subject: "", body: "", noteRecipientId: 0, mailRecipientIds: [] };

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
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [tab, setTab] = useState<"inbox" | "send">("inbox");
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formKey, setFormKey] = useState(0);
  const [error, setError] = useState("");

  const load = () => api<Msg[]>("/messages/inbox").then(setInbox);
  const loadRecipients = () => api<Recipient[]>("/messages/recipients").then(setRecipients);

  useEffect(() => {
    load();
    loadRecipients();
  }, []);

  useEffect(() => {
    if (recipients.length && !form.noteRecipientId) {
      setForm((f) => ({ ...f, noteRecipientId: recipients[0].id }));
    }
  }, [recipients, form.noteRecipientId]);

  function resetSendForm() {
    setForm({
      ...EMPTY_FORM,
      noteRecipientId: recipients[0]?.id ?? 0,
    });
    setPendingFiles([]);
    setFormKey((k) => k + 1);
  }

  function toggleMailRecipient(id: number) {
    setForm((f) => {
      const ids = f.mailRecipientIds.includes(id)
        ? f.mailRecipientIds.filter((x) => x !== id)
        : [...f.mailRecipientIds, id];
      return { ...f, mailRecipientIds: ids };
    });
  }

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

  async function send(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    const recipientIds =
      form.type === "note" ? [form.noteRecipientId] : form.mailRecipientIds;

    if (!recipientIds.length || recipientIds.some((id) => !id)) {
      setError("받는 사람을 선택해 주세요");
      return;
    }
    if (!form.body.trim()) {
      setError("내용을 입력해 주세요");
      return;
    }

    try {
      await api("/messages", {
        method: "POST",
        body: JSON.stringify({
          type: form.type,
          recipient_ids: recipientIds,
          subject: form.subject.trim(),
          body: form.body.trim(),
          attachments: pendingFiles.map(({ filename, content_type, data_base64 }) => ({
            filename,
            content_type,
            data_base64,
          })),
        }),
      });
      resetSendForm();
      setTab("inbox");
      load();
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
        <form key={formKey} className="card" onSubmit={send} style={{ marginTop: "1rem" }}>
          <label className="label">종류</label>
          <select
            className="field"
            value={form.type}
            onChange={(e) => setForm((f) => ({ ...f, type: e.target.value as "note" | "mail" }))}
          >
            <option value="note">쪽지 (1명)</option>
            <option value="mail">메일 (여러 명)</option>
          </select>

          {recipients.length === 0 ? (
            <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>보낼 수 있는 받는 사람이 없습니다.</p>
          ) : form.type === "note" ? (
            <>
              <label className="label">받는 사람</label>
              <select
                className="field"
                value={form.noteRecipientId}
                onChange={(e) => setForm((f) => ({ ...f, noteRecipientId: Number(e.target.value) }))}
              >
                {recipients.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.rank.name} {u.name} ({u.login_id})
                  </option>
                ))}
              </select>
            </>
          ) : (
            <>
              <label className="label">받는 사람 (여러 명 선택)</label>
              <div className="card" style={{ padding: "0.75rem", marginBottom: "0.5rem" }}>
                {recipients.map((u) => (
                  <label key={u.id} style={{ display: "block", marginBottom: "0.35rem", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={form.mailRecipientIds.includes(u.id)}
                      onChange={() => toggleMailRecipient(u.id)}
                      style={{ marginRight: "0.5rem" }}
                    />
                    {u.rank.name} {u.name} ({u.login_id})
                  </label>
                ))}
              </div>
            </>
          )}

          <label className="label">제목</label>
          <input
            className="field"
            value={form.subject}
            onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))}
          />
          <label className="label">내용</label>
          <textarea
            className="field"
            rows={4}
            required
            value={form.body}
            onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
          />
          <label className="label">첨부파일 (사진·문서, 최대 5개·각 5MB)</label>
          <input
            type="file"
            className="field"
            multiple
            accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip"
            onChange={onFilesSelected}
          />
          {pendingFiles.length > 0 && (
            <ul style={{ margin: "0.5rem 0", paddingLeft: "1.2rem", fontSize: "0.9rem" }}>
              {pendingFiles.map((f, i) => (
                <li key={`${f.filename}-${i}`}>
                  {f.filename} ({formatSize(f.size_bytes)}){" "}
                  <button
                    type="button"
                    className="btn btn-ghost"
                    style={{ padding: "0 0.4rem" }}
                    onClick={() => setPendingFiles((p) => p.filter((_, j) => j !== i))}
                  >
                    삭제
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button type="submit" className="btn btn-primary" disabled={recipients.length === 0}>
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
