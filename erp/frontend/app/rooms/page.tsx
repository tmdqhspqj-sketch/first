"use client";

import { useEffect, useMemo, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, User } from "@/lib/api";

type Room = { id: number; name: string; capacity: number };
type Booking = {
  id: number;
  title: string;
  start_at: string;
  end_at: string;
  room: Room;
  user: User;
};

const TIME_SLOTS = Array.from({ length: 48 }, (_, i) => {
  const h = String(Math.floor(i / 2)).padStart(2, "0");
  const m = i % 2 === 0 ? "00" : "30";
  return `${h}:${m}`;
});

function formatMonthDay(iso: string) {
  const d = new Date(iso);
  return `${d.getMonth() + 1}월 ${d.getDate()}일`;
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", hour12: false });
}

function bookerLabel(user: User) {
  const rank = user.rank?.name ?? "";
  return rank ? `${rank} ${user.name}` : user.name;
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [error, setError] = useState("");

  const load = () => {
    api<Room[]>("/rooms").then(setRooms);
    api<Booking[]>("/rooms/bookings").then(setBookings);
  };

  useEffect(() => {
    load();
  }, []);

  const sortedBookings = useMemo(
    () => [...bookings].sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime()),
    [bookings]
  );

  async function book(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const fd = new FormData(e.currentTarget);
    const date = String(fd.get("date"));
    const startTime = String(fd.get("start_time"));
    const durationMin = Number(fd.get("duration"));
    const start = new Date(`${date}T${startTime}:00`);
    const end = new Date(start.getTime() + durationMin * 60 * 1000);

    try {
      await api("/rooms/bookings", {
        method: "POST",
        body: JSON.stringify({
          room_id: Number(fd.get("room_id")),
          title: fd.get("title"),
          start_at: start.toISOString(),
          end_at: end.toISOString(),
        }),
      });
      load();
      e.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "예약 실패");
    }
  }

  return (
    <AppShell>
      <h1>회의실 예약</h1>
      <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
        시작 시간은 30분 단위 · 예약 시간 30분 또는 1시간
      </p>
      {error && <p className="error">{error}</p>}
      <form className="card" onSubmit={book}>
        <label className="label">회의실</label>
        <select name="room_id" className="field" required>
          {rooms.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name} ({r.capacity}명)
            </option>
          ))}
        </select>
        <label className="label">제목</label>
        <input name="title" className="field" required />
        <label className="label">날짜</label>
        <input name="date" type="date" className="field" required />
        <label className="label">시작 시간 (30분 단위)</label>
        <select name="start_time" className="field" required>
          {TIME_SLOTS.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <label className="label">예약 시간</label>
        <select name="duration" className="field" required defaultValue="30">
          <option value="30">30분</option>
          <option value="60">1시간</option>
        </select>
        <button type="submit" className="btn btn-primary">
          예약
        </button>
      </form>
      <div className="card">
        <h3>예약 목록</h3>
        <table>
          <thead>
            <tr>
              <th>날짜</th>
              <th>회의실</th>
              <th>제목</th>
              <th>시간</th>
              <th>예약자</th>
            </tr>
          </thead>
          <tbody>
            {sortedBookings.map((b) => (
              <tr key={b.id}>
                <td>{formatMonthDay(b.start_at)}</td>
                <td>{b.room.name}</td>
                <td>{b.title}</td>
                <td>
                  {formatTime(b.start_at)} ~ {formatTime(b.end_at)}
                </td>
                <td>{bookerLabel(b.user)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {sortedBookings.length === 0 && <p style={{ color: "var(--muted)" }}>예약이 없습니다.</p>}
      </div>
    </AppShell>
  );
}
