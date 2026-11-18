import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import login, require_admin
from .storage import load, save, update_by_id
from .stages import STAGES, stages_skipped
from .seed import seed_enquiries, clear_seed
from .config import ADMIN_PASSWORD


router = APIRouter(prefix="/api/admin", tags=["admin"])
_login_attempts: dict[str, deque[float]] = defaultdict(deque)


class LoginRequest(BaseModel):
    email: str


class EnquiryPatch(BaseModel):
    stage: int | None = None
    status: str | None = None
    internal_note: str | None = None


@router.post("/login")
def admin_login(payload: LoginRequest):
    email = payload.email.strip().lower()
    key = email
    now = time.monotonic()
    bucket = _login_attempts[key]
    while bucket and now - bucket[0] > 300:
        bucket.popleft()
    if len(bucket) >= 8:
        raise HTTPException(429, "Too many login attempts. Please try again later.")
    bucket.append(now)
    from .config import ADMIN_EMAIL
    if email != ADMIN_EMAIL:
        raise HTTPException(401, "This email is not authorized for admin access.")
    return {"token": login(ADMIN_PASSWORD), "expires_in": 28800}


@router.get("/enquiries")
def list_enquiries(
    type: str = "",
    stage: str = "",
    status: str = "",
    search: str = "",
    _admin: bool = Depends(require_admin),
):
    items = load("enquiries", [])
    needle = search.lower()
    filtered = []
    for item in items:
        if type and item["enquiry_type"] != type:
            continue
        if stage and str(item["current_stage"]) != stage:
            continue
        if status and item["status"] != status:
            continue
        searchable = " ".join(str(value) for value in item.values()).lower()
        if needle and needle not in searchable:
            continue
        filtered.append(item)
    return filtered
