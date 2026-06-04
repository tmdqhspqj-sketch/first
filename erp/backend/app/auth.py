from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import User

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, login_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.token_expire_hours)
    payload = {"sub": str(user_id), "login_id": login_id, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not creds or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        data = jwt.decode(creds.credentials, settings.secret_key, algorithms=["HS256"])
        user_id = int(data["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from None
    user = db.query(User).options(joinedload(User.rank)).filter(User.id == user_id).first()
    if not user or not user.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User inactive")
    return user


def require_super(user: User = Depends(get_current_user)) -> User:
    if user.role != "super":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Super only")
    return user


def rank_level(user: User) -> int:
    return user.rank.level if user.rank else 0
