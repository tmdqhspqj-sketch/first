from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Message, MessageRecipient, MessageType, User
from app.schemas import MessageCreateIn, MessageOut

router = APIRouter(prefix="/messages", tags=["messages"])


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
    msg = Message(
        type=body.type,
        sender_id=user.id,
        subject=body.subject or ("쪽지" if body.type == "note" else ""),
        body=body.body,
    )
    db.add(msg)
    db.flush()
    for rid in body.recipient_ids:
        if not db.get(User, rid):
            raise HTTPException(404, f"User {rid} not found")
        db.add(MessageRecipient(message_id=msg.id, recipient_id=rid))
    db.commit()
    return MessageOut(
        id=msg.id,
        type=msg.type,
        subject=msg.subject,
        body=msg.body,
        sender=user,
        created_at=msg.created_at,
    )


@router.get("/inbox", response_model=list[MessageOut])
def inbox(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(MessageRecipient, Message)
        .join(Message, MessageRecipient.message_id == Message.id)
        .options(joinedload(Message.sender).joinedload(User.rank))
        .filter(MessageRecipient.recipient_id == user.id)
        .order_by(Message.id.desc())
        .all()
    )
    out = []
    for rec, msg in rows:
        out.append(
            MessageOut(
                id=msg.id,
                type=msg.type,
                subject=msg.subject,
                body=msg.body,
                sender=msg.sender,
                created_at=msg.created_at,
                read_at=rec.read_at,
            )
        )
    return out


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
