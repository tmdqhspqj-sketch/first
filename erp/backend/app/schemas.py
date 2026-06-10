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


class AdminOut(BaseModel):
    id: int
    login_id: str
    name: str
    active: bool
    deactivated_at: datetime | None = None
    created_at: datetime


class AdminCreateIn(BaseModel):
    login_id: str
    password: str
    name: str


class AdminUpdateIn(BaseModel):
    name: str | None = None
    password: str | None = None


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


class AttachmentIn(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(default="application/octet-stream", max_length=128)
    data_base64: str = Field(min_length=1)


class AttachmentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int

    class Config:
        from_attributes = True


class MessageCreateIn(BaseModel):
    type: str = Field(pattern="^(note|mail)$")
    recipient_ids: list[int]
    subject: str = ""
    body: str = Field(min_length=1)
    attachments: list[AttachmentIn] = Field(default_factory=list)


class MessageOut(BaseModel):
    id: int
    type: str
    subject: str
    body: str
    sender: UserOut
    created_at: datetime
    read_at: datetime | None = None
    archived: bool = False
    important: bool = False
    attachments: list[AttachmentOut] = Field(default_factory=list)

    class Config:
        from_attributes = True
