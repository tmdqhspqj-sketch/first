const API = process.env.NEXT_PUBLIC_ERP_API_URL ?? "http://127.0.0.1:8001";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("erp_token");
}

export function setToken(t: string) {
  localStorage.setItem("erp_token", t);
}

export function clearToken() {
  localStorage.removeItem("erp_token");
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

export type User = {
  id: number;
  login_id: string;
  name: string;
  role: string;
  rank: { id: number; name: string; level: number };
};

export type Approval = {
  id: number;
  type: string;
  status: string;
  title: string;
  body: string;
  leave_kind?: string;
  leave_start?: string;
  leave_end?: string;
  idea_summary?: string;
  reject_reason?: string;
  requester: User;
  created_at: string;
};
