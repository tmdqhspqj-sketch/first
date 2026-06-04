from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user, hash_password
from app.database import get_db
from app.models import Rank, User
from app.schemas import UserCreateIn, UserOut
from app.services.permissions import assert_can_manage, can_manage_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), actor: User = Depends(get_current_user)):
    q = db.query(User).options(joinedload(User.rank)).filter(User.active.is_(True))
    if actor.role == "manager":
        q = q.filter(User.rank.has(Rank.level < actor.rank.level))
    elif actor.role == "user":
        q = q.filter(User.id == actor.id)
    return q.order_by(User.id).all()


@router.post("", response_model=UserOut)
def create_user(body: UserCreateIn, db: Session = Depends(get_db), actor: User = Depends(get_current_user)):
    rank = db.get(Rank, body.rank_id)
    if not rank:
        raise HTTPException(404, "Rank not found")
    if not can_manage_user(actor, rank.level):
        raise HTTPException(403, "Cannot create user at this rank")
    if db.query(User).filter(User.login_id == body.login_id).first():
        raise HTTPException(400, "Login ID exists")
    from app.seed import role_for_rank

    user = User(
        login_id=body.login_id,
        password_hash=hash_password(body.password),
        name=body.name,
        rank_id=rank.id,
        role=role_for_rank(rank.name) if actor.role != "super" else role_for_rank(rank.name),
        active=True,
    )
    if actor.role == "super" and body.login_id != actor.login_id:
        user.role = role_for_rank(rank.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return db.query(User).options(joinedload(User.rank)).filter(User.id == user.id).one()


@router.get("/ranks", response_model=list)
def list_ranks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return [{"id": r.id, "name": r.name, "level": r.level} for r in db.query(Rank).order_by(Rank.level.desc()).all()]
