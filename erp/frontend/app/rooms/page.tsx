"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

type Room = { id: number; name: string; capacity: number };
type Booking = {
  id: number;
  title: string;
  start_at: string;
  end_at: string;
  room: Room;
  user: { name: string };
};

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);

  const load = () => {
    api<Room[]>("/rooms").then(setRooms);
    api<Booking[]>("/rooms/bookings").then(setBookings);
  };

  useEffect(() => {
    load();
  }, []);

  async function book(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const start = `${fd.get("date")}T${fd.get("start_time")}:00`;
    const end = `${fd.get("date")}T${fd.get("end_time")}:00`;
    await api("/rooms/bookings", {
      method: "POST",
      body: JSON.stringify({
        room_id: Number(fd.get("room_id")),
        title: fd.get("title"),
        start_at: start,
        end_at: end,
      }),
    });
    load();
    e.currentTarget.reset();
  }

  return (
    <AppShell>
      <h1>회의실 예약</h1>
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
        <label className="label">시작</label>
        <input name="start_time" type="time" className="field" required />
        <label className="label">종료</label>
        <input name="end_time" type="time" className="field" required />
        <button type="submit" className="btn btn-primary">
          예약
        </button>
      </form>
      <div className="card">
        <h3>예약 목록</h3>
        <table>
          <thead>
            <tr>
              <th>회의실</th>
              <th>제목</th>
              <th>시간</th>
              <th>예약자</th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((b) => (
              <tr key={b.id}>
                <td>{b.room.name}</td>
                <td>{b.title}</td>
                <td>
                  {new Date(b.start_at).toLocaleString("ko")} ~{" "}
                  {new Date(b.end_at).toLocaleTimeString("ko", { hour: "2-digit", minute: "2-digit" })}
                </td>
                <td>{b.user.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
