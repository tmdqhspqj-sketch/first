from fastapi import HTTPException, status

from app.models import User


def can_manage_user(actor: User, target_rank_level: int) -> bool:
    if actor.role == "super":
        return True
    if actor.role == "manager":
        return target_rank_level < actor.rank.level
    return False


def assert_can_manage(actor: User, target: User) -> None:
    if actor.id == target.id:
        return
    if not can_manage_user(actor, target.rank.level):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot manage this user")
