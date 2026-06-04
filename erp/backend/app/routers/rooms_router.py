from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import MeetingRoom, RoomBooking, User
from app.schemas import BookingCreateIn, BookingOut, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(MeetingRoom).filter(MeetingRoom.active.is_(True)).all()


@router.get("/bookings", response_model=list[BookingOut])
def list_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = (
        db.query(RoomBooking)
        .options(joinedload(RoomBooking.room), joinedload(RoomBooking.user).joinedload(User.rank))
        .order_by(RoomBooking.start_at)
    )
    if user.role != "super":
        q = q.filter(RoomBooking.user_id == user.id)
    return q.all()


@router.post("/bookings", response_model=BookingOut)
def create_booking(
    body: BookingCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.end_at <= body.start_at:
        raise HTTPException(400, "end must be after start")
    overlap = (
        db.query(RoomBooking)
        .filter(
            RoomBooking.room_id == body.room_id,
            RoomBooking.start_at < body.end_at,
            RoomBooking.end_at > body.start_at,
        )
        .first()
    )
    if overlap:
        raise HTTPException(409, "Room already booked")
    b = RoomBooking(
        room_id=body.room_id,
        user_id=user.id,
        title=body.title,
        start_at=body.start_at,
        end_at=body.end_at,
    )
    db.add(b)
    db.commit()
    return (
        db.query(RoomBooking)
        .options(joinedload(RoomBooking.room), joinedload(RoomBooking.user).joinedload(User.rank))
        .filter(RoomBooking.id == b.id)
        .one()
    )


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = db.get(RoomBooking, booking_id)
    if not b:
        raise HTTPException(404, "Not found")
    if user.role != "super" and b.user_id != user.id:
        raise HTTPException(403, "Not yours")
    db.delete(b)
    db.commit()
    return {"ok": True}
