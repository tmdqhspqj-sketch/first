"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, Approval, User } from "@/lib/api";

const STATUS_KO: Record<string, string> = {
  draft: "작성중",
  pending_bujang: "팀장(부장) 대기",
  pending_sangmu: "상무 대기",
  pending_sajang: "사장 대기",
  approved: "승인완료",
  rejected: "반려",
};

export default function ApprovalsPage() {
  const [me, setMe] = useState<User | null>(null);
  const [list, setList] = useState<Approval[]>([]);
  const [inbox, setInbox] = useState<Approval[]>([]);
  const [tab, setTab] = useState<"list" | "leave" | "idea">("list");
  const [error, setError] = useState("");

  const load = () => {
    api<Approval[]>("/approvals").then(setList);
    api<Approval[]>("/approvals/inbox")
      .then(setInbox)
      .catch(() => setInbox([]));
  };

  useEffect(() => {
    api<User>("/auth/me").then(setMe);
    load();
  }, []);

  async function createLeave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      const created = await api<Approval>("/approvals/leave", {
        method: "POST",
        body: JSON.stringify({
          leave_kind: fd.get("kind"),
          leave_start: fd.get("start"),
          leave_end: fd.get("end"),
          body: fd.get("body"),
        }),
      });
      await api(`/approvals/${created.id}/submit`, { method: "POST" });
      setTab("list");
      load();
    } catch (err) {
      setError(String(err));
    }
  }

  async function createIdea(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      const created = await api<Approval>("/approvals/product-idea", {
        method: "POST",
        body: JSON.stringify({
          title: fd.get("title"),
          idea_summary: fd.get("summary"),
          body: fd.get("body"),
        }),
      });
      await api(`/approvals/${created.id}/submit`, { method: "POST" });
      setTab("list");
      load();
    } catch (err) {
      setError(String(err));
    }
  }

  async function approve(id: number) {
    await api(`/approvals/${id}/approve`, { method: "POST" });
    load();
  }

  async function reject(id: number) {
    const reason = prompt("반려 사유");
    if (!reason) return;
    await api(`/approvals/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
    load();
  }

  const canApprove = me && me.role !== "admin";

  return (
    <AppShell>
      <h1>결재</h1>
      <div style={{ marginBottom: "1rem" }}>
        <button type="button" className="btn btn-ghost" onClick={() => setTab("list")}>
          목록
        </button>{" "}
        <button type="button" className="btn btn-ghost" onClick={() => setTab("leave")}>
          휴가 신청
        </button>{" "}
        <button type="button" className="btn btn-ghost" onClick={() => setTab("idea")}>
          상품 아이디어
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      {tab === "leave" && (
        <form className="card" onSubmit={createLeave}>
          <h3>휴가 신청</h3>
          <label className="label">종류</label>
          <select name="kind" className="field" defaultValue="연차">
            <option>연차</option>
            <option>반차</option>
            <option>병가</option>
          </select>
          <label className="label">시작일</label>
          <input name="start" type="date" className="field" required />
          <label className="label">종료일</label>
          <input name="end" type="date" className="field" required />
          <label className="label">사유</label>
          <textarea name="body" className="field" rows={3} />
          <button type="submit" className="btn btn-primary">
            상신
          </button>
        </form>
      )}

      {tab === "idea" && me && (
        <form className="card" onSubmit={createIdea}>
          <h3>상품 아이디어 신청</h3>
          <p>
            신청자: <strong>{me.name}</strong> · 직급: <strong>{me.rank.name}</strong>
          </p>
          <label className="label">제목</label>
          <input name="title" className="field" required />
          <label className="label">아이디어 요약</label>
          <input name="summary" className="field" required />
          <label className="label">상세</label>
          <textarea name="body" className="field" rows={4} />
          <button type="submit" className="btn btn-primary">
            상신
          </button>
        </form>
      )}

      {tab === "list" && (
        <>
          {canApprove && inbox.length > 0 && (
            <div className="card">
              <h3>승인할 문서</h3>
              <table>
                <thead>
                  <tr>
                    <th>제목</th>
                    <th>신청자</th>
                    <th>상태</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {inbox.map((a) => (
                    <tr key={a.id}>
                      <td>{a.title}</td>
                      <td>
                        {a.requester.name} ({a.requester.rank.name})
                      </td>
                      <td>{STATUS_KO[a.status] ?? a.status}</td>
                      <td>
                        <button type="button" className="btn btn-primary" onClick={() => approve(a.id)}>
                          승인
                        </button>{" "}
                        <button type="button" className="btn btn-danger" onClick={() => reject(a.id)}>
                          반려
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="card">
            <h3>{me?.role === "admin" ? "전체 결재 관람" : "결재 목록"}</h3>
            <table>
              <thead>
                <tr>
                  <th>유형</th>
                  <th>제목</th>
                  <th>신청자</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {list.map((a) => (
                  <tr key={a.id}>
                    <td>{a.type === "leave" ? "휴가" : "아이디어"}</td>
                    <td>{a.title}</td>
                    <td>
                      {a.requester.name} ({a.requester.rank.name})
                    </td>
                    <td>{STATUS_KO[a.status] ?? a.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </AppShell>
  );
}
