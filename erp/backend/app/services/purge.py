import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import User, UserRole

logger = logging.getLogger(__name__)


def purge_deactivated_users(db: Session) -> int:
    cutoff = datetime.utcnow() - timedelta(days=settings.deactivate_purge_days)
    stale = (
        db.query(User)
        .filter(
            User.active.is_(False),
            User.deactivated_at.isnot(None),
            User.deactivated_at <= cutoff,
        )
        .all()
    )
    if not stale:
        return 0
    for user in stale:
        db.delete(user)
    db.commit()
    logger.info("Purged %s deactivated user(s)", len(stale))
    return len(stale)


def count_active_admins(db: Session) -> int:
    return (
        db.query(User)
        .filter(User.role == UserRole.admin.value, User.active.is_(True))
        .count()
    )


async def purge_loop() -> None:
    interval = max(settings.purge_interval_hours, 1) * 3600
    while True:
        try:
            db = SessionLocal()
            try:
                purge_deactivated_users(db)
            finally:
                db.close()
        except Exception:
            logger.exception("Purge job failed")
        await asyncio.sleep(interval)
