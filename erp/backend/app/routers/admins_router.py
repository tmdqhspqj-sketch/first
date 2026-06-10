from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import hash_password, require_admin
from app.database import get_db
from app.models import Rank, User, UserRole
from app.schemas import AdminCreateIn, AdminOut, AdminUpdateIn
from app.services.purge import count_active_admins

router = APIRouter(prefix="/admins", tags=["admins"])


def _admin_out(user: User) -> AdminOut:
    return AdminOut(
        id=user.id,
        login_id=user.login_id,
        name=user.name,
        active=user.active,
        deactivated_at=user.deactivated_at,
        created_at=user.created_at,
    )


@router.get("", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    admins = (
        db.query(User)
        .filter(User.role == UserRole.admin.value)
        .order_by(User.id)
        .all()
    )
    return [_admin_out(a) for a in admins]


@router.post("", response_model=AdminOut)
def create_admin(body: AdminCreateIn, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(User).filter(User.login_id == body.login_id).first():
        raise HTTPException(400, "Login ID exists")
    rank = db.query(Rank).filter(Rank.name == "사장").first()
    if not rank:
        raise HTTPException(500, "Rank data missing")
    user = User(
        login_id=body.login_id,
        password_hash=hash_password(body.password),
        name=body.name,
        rank_id=rank.id,
        role=UserRole.admin.value,
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _admin_out(user)


@router.patch("/{admin_id}", response_model=AdminOut)
def update_admin(
    admin_id: int,
    body: AdminUpdateIn,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    user = db.get(User, admin_id)
    if not user or user.role != UserRole.admin.value:
        raise HTTPException(404, "Admin not found")
    if body.name is not None:
        user.name = body.name
    if body.password is not None:
        user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    return _admin_out(user)


@router.post("/{admin_id}/deactivate", response_model=AdminOut)
def deactivate_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    if actor.id == admin_id:
        raise HTTPException(400, "Cannot deactivate yourself")
    user = db.get(User, admin_id)
    if not user or user.role != UserRole.admin.value:
        raise HTTPException(404, "Admin not found")
    if not user.active:
        return _admin_out(user)
    if count_active_admins(db) <= 1:
        raise HTTPException(400, "Cannot deactivate the last active admin")
    user.active = False
    user.deactivated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return _admin_out(user)


@router.post("/{admin_id}/activate", response_model=AdminOut)
def activate_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, admin_id)
    if not user or user.role != UserRole.admin.value:
        raise HTTPException(404, "Admin not found")
    user.active = True
    user.deactivated_at = None
    db.commit()
    db.refresh(user)
    return _admin_out(user)
