import base64
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.auth import _user_from_jwt, get_current_user, get_optional_user
from app.database import get_db
from app.models import Message, MessageAttachment, MessageRecipient, MessageType, User
from app.schemas import AttachmentOut, MessageCreateIn, MessageOut
from app.services.attachments import decode_attachment, validate_attachments

router = APIRouter(prefix="/messages", tags=["messages"])


def _message_out(msg: Message, read_at: datetime | None = None) -> MessageOut:
    return MessageOut(
        id=msg.id,
        type=msg.type,
        subject=msg.subject,
        body=msg.body,
        sender=msg.sender,
        created_at=msg.created_at,
        read_at=read_at,
        attachments=[AttachmentOut.model_validate(a) for a in msg.attachments],
    )


@router.get("/recipients", response_model=list)
def list_recipients(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    others = (
        db.query(User)
        .options(joinedload(User.rank))
        .filter(User.active.is_(True), User.id != user.id)
        .order_by(User.id)
        .all()
    )
    return [
        {
            "id": u.id,
            "login_id": u.login_id,
            "name": u.name,
            "rank": {"id": u.rank.id, "name": u.rank.name, "level": u.rank.level},
        }
        for u in others
    ]


@router.post("", response_model=MessageOut)
def send_message(
    body: MessageCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.type == MessageType.note.value and len(body.recipient_ids) != 1:
        raise HTTPException(400, "Note requires exactly one recipient")
    if not body.recipient_ids:
        raise HTTPException(400, "No recipients")
    validate_attachments(body.attachments)

    msg = Message(
        type=body.type,
        sender_id=user.id,
        subject=body.subject or ("쪽지" if body.type == "note" else ""),
        body=body.body,
    )
    db.add(msg)
    db.flush()

    for att in body.attachments:
        data = decode_attachment(att.data_base64)
        db.add(
            MessageAttachment(
                message_id=msg.id,
                filename=att.filename,
                content_type=att.content_type or "application/octet-stream",
                data_base64=base64.b64encode(data).decode("ascii"),
                size_bytes=len(data),
            )
        )

    for rid in body.recipient_ids:
        if not db.get(User, rid):
            raise HTTPException(404, f"User {rid} not found")
        db.add(MessageRecipient(message_id=msg.id, recipient_id=rid))
    db.commit()

    msg = (
        db.query(Message)
        .options(
            joinedload(Message.sender).joinedload(User.rank),
            joinedload(Message.attachments),
        )
        .filter(Message.id == msg.id)
        .one()
    )
    return _message_out(msg)


@router.get("/inbox", response_model=list[MessageOut])
def inbox(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(MessageRecipient, Message)
        .join(Message, MessageRecipient.message_id == Message.id)
        .options(
            joinedload(Message.sender).joinedload(User.rank),
            joinedload(Message.attachments),
        )
        .filter(MessageRecipient.recipient_id == user.id)
        .order_by(Message.id.desc())
        .all()
    )
    return [_message_out(msg, rec.read_at) for rec, msg in rows]


@router.get("/attachments/{attachment_id}")
def download_attachment(
    attachment_id: int,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
    header_user: User | None = Depends(get_optional_user),
):
    user = header_user or (_user_from_jwt(token, db) if token else None)
    if not user:
        raise HTTPException(401, "Not authenticated")
    att = db.get(MessageAttachment, attachment_id)
    if not att:
        raise HTTPException(404, "Not found")
    allowed = (
        db.query(MessageRecipient)
        .filter(
            MessageRecipient.message_id == att.message_id,
            MessageRecipient.recipient_id == user.id,
        )
        .first()
    )
    msg = db.get(Message, att.message_id)
    if not allowed and (not msg or msg.sender_id != user.id) and user.role != "admin":
        raise HTTPException(403, "Forbidden")
    data = base64.b64decode(att.data_base64)
    return Response(
        content=data,
        media_type=att.content_type,
        headers={"Content-Disposition": f'inline; filename="{att.filename}"'},
    )


@router.post("/{message_id}/read")
def mark_read(message_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rec = (
        db.query(MessageRecipient)
        .filter(MessageRecipient.message_id == message_id, MessageRecipient.recipient_id == user.id)
        .first()
    )
    if not rec:
        raise HTTPException(404, "Not found")
    rec.read_at = datetime.utcnow()
    db.commit()
    return {"ok": True}
