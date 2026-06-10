from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import MeetingRoom, Rank, User, UserRole

RANKS = [
    ("사장", 8),
    ("상무", 7),
    ("이사", 6),
    ("부장", 5),
    ("차장", 4),
    ("과장", 3),
    ("대리", 2),
    ("사원", 1),
]

DEMO_USERS = [
    ("sajang", "김사장", "사장", UserRole.manager.value, "demo1"),
    ("sangmu", "이상무", "상무", UserRole.manager.value, "demo1"),
    ("bujang", "박팀장", "부장", UserRole.user.value, "demo1"),
    ("staff1", "최사원", "사원", UserRole.user.value, "demo1"),
]

ADMIN_USERS = [
    (settings.hong_login, "홍승보", settings.hong_password),
    (settings.admin_login, "시스템관리자", settings.admin_password),
]


def role_for_rank(rank_name: str) -> str:
    if rank_name in ("사장", "상무", "이사"):
        return UserRole.manager.value
    return UserRole.user.value


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if not db.query(Rank).count():
            for name, level in RANKS:
                db.add(Rank(name=name, level=level))
            db.commit()

        ranks = {r.name: r for r in db.query(Rank).all()}

        for login_id, name, pwd in ADMIN_USERS:
            if db.query(User).filter(User.login_id == login_id).first():
                continue
            db.add(
                User(
                    login_id=login_id,
                    password_hash=hash_password(pwd),
                    name=name,
                    rank_id=ranks["사장"].id,
                    role=UserRole.admin.value,
                    active=True,
                )
            )
        db.commit()

        for login_id, name, rank_name, role, pwd in DEMO_USERS:
            if db.query(User).filter(User.login_id == login_id).first():
                continue
            db.add(
                User(
                    login_id=login_id,
                    password_hash=hash_password(pwd),
                    name=name,
                    rank_id=ranks[rank_name].id,
                    role=role,
                    active=True,
                )
            )
        db.commit()

        if not db.query(MeetingRoom).count():
            for n, cap in [("회의실 A", 8), ("회의실 B", 12), ("소회의실", 4)]:
                db.add(MeetingRoom(name=n, capacity=cap))
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
