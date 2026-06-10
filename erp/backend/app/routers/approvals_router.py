from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import ApprovalRequest, ApprovalStatus, ApprovalType, User
from app.schemas import ApprovalOut, LeaveCreateIn, ProductIdeaCreateIn, RejectIn
from app.services.approval_flow import (
    NEXT_STATUS,
    can_approve,
    skip_steps_for_requester,
)

router = APIRouter(prefix="/approvals", tags=["approvals"])


def _to_out(req: ApprovalRequest) -> ApprovalOut:
    return ApprovalOut.model_validate(req)


@router.get("", response_model=list[ApprovalOut])
def list_approvals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank))
    if user.role == "admin":
        return q.order_by(ApprovalRequest.id.desc()).all()
    if user.role == "manager" or user.rank.name == "부장":
        mine = q.filter(ApprovalRequest.requester_id == user.id).all()
        pending = [r for r in q.all() if can_approve(user, r.status)]
        seen = {r.id for r in mine}
        return mine + [r for r in pending if r.id not in seen]
    return q.filter(ApprovalRequest.requester_id == user.id).order_by(ApprovalRequest.id.desc()).all()


@router.get("/inbox", response_model=list[ApprovalOut])
def approval_inbox(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "admin":
        raise HTTPException(403, "Admin cannot approve; use list view")
    items = (
        db.query(ApprovalRequest)
        .options(joinedload(ApprovalRequest.requester).joinedload(User.rank))
        .order_by(ApprovalRequest.id.desc())
        .all()
    )
    return [r for r in items if can_approve(user, r.status)]


@router.post("/leave", response_model=ApprovalOut)
def create_leave(
    body: LeaveCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = ApprovalRequest(
        type=ApprovalType.leave.value,
        status=ApprovalStatus.draft.value,
        requester_id=user.id,
        title=body.title,
        body=body.body,
        leave_kind=body.leave_kind,
        leave_start=body.leave_start,
        leave_end=body.leave_end,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank)).filter(
        ApprovalRequest.id == req.id
    ).one()


@router.post("/product-idea", response_model=ApprovalOut)
def create_product_idea(
    body: ProductIdeaCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    header = f"[신청] {user.name} ({user.rank.name})"
    req = ApprovalRequest(
        type=ApprovalType.product_idea.value,
        status=ApprovalStatus.draft.value,
        requester_id=user.id,
        title=body.title,
        body=body.body,
        idea_summary=body.idea_summary,
    )
    req.title = f"{header} - {body.title}"
    db.add(req)
    db.commit()
    db.refresh(req)
    return db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank)).filter(
        ApprovalRequest.id == req.id
    ).one()


@router.post("/{req_id}/submit", response_model=ApprovalOut)
def submit_request(req_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = db.get(ApprovalRequest, req_id)
    if not req or req.requester_id != user.id:
        raise HTTPException(404, "Not found")
    if req.status != ApprovalStatus.draft.value:
        raise HTTPException(400, "Already submitted")
    req.status = skip_steps_for_requester(user)
    if req.status == ApprovalStatus.approved.value:
        req.updated_at = datetime.utcnow()
    db.commit()
    return db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank)).filter(
        ApprovalRequest.id == req_id
    ).one()


@router.post("/{req_id}/approve", response_model=ApprovalOut)
def approve_request(req_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "admin":
        raise HTTPException(403, "Admin can only view approvals")
    req = db.get(ApprovalRequest, req_id)
    if not req:
        raise HTTPException(404, "Not found")
    if not can_approve(user, req.status):
        raise HTTPException(403, "Not your approval step")
    nxt = NEXT_STATUS.get(req.status)
    if not nxt:
        raise HTTPException(400, "Cannot approve")
    req.status = nxt
    req.updated_at = datetime.utcnow()
    db.commit()
    return db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank)).filter(
        ApprovalRequest.id == req_id
    ).one()


@router.post("/{req_id}/reject", response_model=ApprovalOut)
def reject_request(
    req_id: int,
    body: RejectIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "admin":
        raise HTTPException(403, "Admin can only view approvals")
    req = db.get(ApprovalRequest, req_id)
    if not req:
        raise HTTPException(404, "Not found")
    if not can_approve(user, req.status):
        raise HTTPException(403, "Not your approval step")
    req.status = ApprovalStatus.rejected.value
    req.reject_reason = body.reason
    req.updated_at = datetime.utcnow()
    db.commit()
    return db.query(ApprovalRequest).options(joinedload(ApprovalRequest.requester).joinedload(User.rank)).filter(
        ApprovalRequest.id == req_id
    ).one()
