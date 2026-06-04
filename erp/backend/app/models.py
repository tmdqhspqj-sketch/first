import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    superuser = "super"
    manager = "manager"
    user = "user"


class ApprovalType(str, enum.Enum):
    leave = "leave"
    product_idea = "product_idea"


class ApprovalStatus(str, enum.Enum):
    draft = "draft"
    pending_bujang = "pending_bujang"
    pending_sangmu = "pending_sangmu"
    pending_sajang = "pending_sajang"
    approved = "approved"
    rejected = "rejected"


class MessageType(str, enum.Enum):
    note = "note"
    mail = "mail"


class Rank(Base):
    __tablename__ = "ranks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    level: Mapped[int] = mapped_column(Integer, unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="rank")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(64))
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id"))
    role: Mapped[str] = mapped_column(String(16))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rank: Mapped["Rank"] = relationship(back_populates="users")


class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    capacity: Mapped[int] = mapped_column(Integer, default=8)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class RoomBooking(Base):
    __tablename__ = "room_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("meeting_rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(128))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    room: Mapped["MeetingRoom"] = relationship()
    user: Mapped["User"] = relationship()


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default=ApprovalStatus.draft.value)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    # leave
    leave_start: Mapped[str | None] = mapped_column(String(32), nullable=True)
    leave_end: Mapped[str | None] = mapped_column(String(32), nullable=True)
    leave_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # product idea (requester name/rank snapshot)
    idea_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester: Mapped["User"] = relationship()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(16))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(200), default="")
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sender: Mapped["User"] = relationship(foreign_keys=[sender_id])


class MessageRecipient(Base):
    __tablename__ = "message_recipients"
    __table_args__ = (UniqueConstraint("message_id", "recipient_id", name="uq_msg_recipient"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    message: Mapped["Message"] = relationship()
    recipient: Mapped["User"] = relationship()
