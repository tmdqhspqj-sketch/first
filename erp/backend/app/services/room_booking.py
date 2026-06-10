from datetime import datetime, timedelta

from fastapi import HTTPException

ALLOWED_DURATIONS = {30, 60}


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
