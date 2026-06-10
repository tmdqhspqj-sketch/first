from datetime import datetime, time, timedelta

from fastapi import HTTPException

ALLOWED_DURATIONS = {30, 60}
WORK_START = time(9, 0)
WORK_END = time(17, 0)
RANK_NO_BOOKING = "임시"


def can_book_room(rank_name: str) -> bool:
    return rank_name != RANK_NO_BOOKING


def validate_booking_window(start_at: datetime, end_at: datetime) -> None:
    if end_at <= start_at:
        raise HTTPException(400, "종료 시간은 시작 시간보다 뒤여야 합니다")
    if start_at.second or start_at.microsecond or end_at.second or end_at.microsecond:
        raise HTTPException(400, "시간은 분 단위로만 예약할 수 있습니다")
    if start_at.minute not in (0, 30):
        raise HTTPException(400, "시작 시간은 30분 단위(00분/30분)만 가능합니다")
    duration = int((end_at - start_at).total_seconds() / 60)
    if duration not in ALLOWED_DURATIONS:
        raise HTTPException(400, "예약 시간은 30분 또는 1시간만 가능합니다")
    expected_end = start_at + timedelta(minutes=duration)
    if end_at != expected_end:
        raise HTTPException(400, "예약 시간이 올바르지 않습니다")
    start_t = start_at.time().replace(second=0, microsecond=0)
    end_t = end_at.time().replace(second=0, microsecond=0)
    if start_t < WORK_START or end_t > WORK_END:
        raise HTTPException(400, "회의실 예약은 일과시간 09:00~17:00만 가능합니다")
