import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.purge import purge_deactivated_users

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/purge")
def cron_purge(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    secret = os.environ.get("ERP_CRON_SECRET") or os.environ.get("CRON_SECRET")
    if secret and authorization != f"Bearer {secret}":
        raise HTTPException(403, "Forbidden")
    count = purge_deactivated_users(db)
    return {"purged": count}
