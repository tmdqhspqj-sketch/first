from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import create_token, get_current_user, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.rank))
        .filter(User.login_id == body.login_id, User.active.is_(True))
        .first()
    )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenOut(access_token=create_token(user.id, user.login_id, user.role))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
