from datetime import datetime

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    login_id: str
    password: str


class RankOut(BaseModel):
    id: int
    name: str
    level: int

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    login_id: str
    name: str
    role: str
    rank: RankOut
    active: bool

    class Config:
        from_attributes = True


class UserCreateIn(BaseModel):
    login_id: str
    password: str
    name: str
    rank_id: int


class LeaveCreateIn(BaseModel):
    title: str = "휴가 신청"
    leave_kind: str = "연차"
    leave_start: str
    leave_end: str
    body: str = ""


class ProductIdeaCreateIn(BaseModel):
    title: str
    idea_summary: str
    body: str = ""


class ApprovalOut(BaseModel):
    id: int
    type: str
    status: str
    title: str
    body: str
    leave_kind: str | None
    leave_start: str | None
    leave_end: str | None
    idea_summary: str | None
    reject_reason: str | None
    requester: UserOut
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RejectIn(BaseModel):
    reason: str = Field(min_length=1)


class RoomOut(BaseModel):
    id: int
    name: str
    capacity: int

    class Config:
        from_attributes = True


class BookingCreateIn(BaseModel):
    room_id: int
    title: str
    start_at: datetime
    end_at: datetime


class BookingOut(BaseModel):
    id: int
    room_id: int
    title: str
    start_at: datetime
    end_at: datetime
    room: RoomOut
    user: UserOut

    class Config:
        from_attributes = True


class MessageCreateIn(BaseModel):
    type: str = Field(pattern="^(note|mail)$")
    recipient_ids: list[int]
    subject: str = ""
    body: str = Field(min_length=1)


class MessageOut(BaseModel):
    id: int
    type: str
    subject: str
    body: str
    sender: UserOut
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True
