import logging
from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Message, MessageAttachment, MessageRecipient

logger = logging.getLogger(__name__)

RETENTION_DAYS = 14


def retention_cutoff() -> datetime:
    return datetime.utcnow() - timedelta(days=RETENTION_DAYS)


def visible_recipient_filter(user_id: int, cutoff: datetime):
    return (
        MessageRecipient.recipient_id == user_id,
        MessageRecipient.deleted_at.is_(None),
        or_(
            MessageRecipient.important.is_(True),
            MessageRecipient.archived.is_(True),
            Message.created_at >= cutoff,
        ),
    )


def purge_expired_messages(db: Session) -> int:
    cutoff = retention_cutoff()
    stale = db.query(Message).filter(Message.created_at < cutoff).all()
    removed = 0
    for msg in stale:
        recs = db.query(MessageRecipient).filter(MessageRecipient.message_id == msg.id).all()
        if any(r.important or r.archived for r in recs):
            continue
        db.query(MessageAttachment).filter(MessageAttachment.message_id == msg.id).delete()
        db.query(MessageRecipient).filter(MessageRecipient.message_id == msg.id).delete()
        db.delete(msg)
        removed += 1
    if removed:
        db.commit()
        logger.info("Purged %s expired message(s)", removed)
    return removed
