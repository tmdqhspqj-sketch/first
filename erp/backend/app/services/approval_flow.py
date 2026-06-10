"""Approval line: 부장(팀장) -> 상무 -> 사장. Super is view-only."""

from app.models import ApprovalStatus, User

RANK_BUJANG = "부장"
RANK_SANGMU = "상무"
RANK_SAJANG = "사장"

NEXT_STATUS = {
    ApprovalStatus.pending_bujang.value: ApprovalStatus.pending_sangmu.value,
    ApprovalStatus.pending_sangmu.value: ApprovalStatus.pending_sajang.value,
    ApprovalStatus.pending_sajang.value: ApprovalStatus.approved.value,
}

STATUS_TO_RANK = {
    ApprovalStatus.pending_bujang.value: RANK_BUJANG,
    ApprovalStatus.pending_sangmu.value: RANK_SANGMU,
    ApprovalStatus.pending_sajang.value: RANK_SAJANG,
}


def can_approve(user: User, status: str) -> bool:
    if user.role == "admin":
        return False
    required_rank = STATUS_TO_RANK.get(status)
    if not required_rank:
        return False
    return user.rank.name == required_rank


def skip_steps_for_requester(requester: User) -> str:
    """If requester is high rank, skip their level and below in chain."""
    name = requester.rank.name
    if name == RANK_SAJANG:
        return ApprovalStatus.approved.value
    if name == RANK_SANGMU:
        return ApprovalStatus.pending_sajang.value
    if name == RANK_BUJANG:
        return ApprovalStatus.pending_sangmu.value
    return ApprovalStatus.pending_bujang.value
