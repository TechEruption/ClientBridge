from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import require_admin
from .storage import load, save, update_by_id
from .stages import STAGES, stages_skipped
from .seed import seed_enquiries, clear_seed


router = APIRouter(prefix="/api/admin", tags=["admin"])


class EnquiryPatch(BaseModel):
    stage: int | None = None
    status: str | None = None
    internal_note: str | None = None


@router.get("/enquiries/{enquiry_id}")
def enquiry_detail(enquiry_id: str, _admin: bool = Depends(require_admin)):
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry:
        raise HTTPException(404, "Enquiry not found.")
    messages = [item for item in load("messages", []) if item["enquiry_id"] == enquiry_id]
    chats = load("chats", [])
    chat = next((item for item in chats if item["session_id"] == enquiry.get("session_id")), None)
    for message in messages:
        if message["direction"] == "in":
            message["unread"] = False
    all_messages = load("messages", [])
    for message in all_messages:
        if message["enquiry_id"] == enquiry_id and message["direction"] == "in":
            message["unread"] = False
    save("messages", all_messages)
    update_by_id("enquiries", enquiry_id, {"has_unread_reply": False})
    return {**enquiry, "messages": messages, "chat": chat}


@router.patch("/enquiries/{enquiry_id}")
def patch_enquiry(enquiry_id: str, payload: EnquiryPatch, _admin: bool = Depends(require_admin)):
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry:
        raise HTTPException(404, "Enquiry not found.")
    changes = {}
    if payload.status:
        changes["status"] = payload.status
    if payload.internal_note is not None:
        changes["internal_note"] = payload.internal_note
        changes["admin_notes"] = enquiry.get("admin_notes", []) + [{
            "note": payload.internal_note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
    if payload.stage is not None:
        if payload.stage < 1 or payload.stage > 6:
            raise HTTPException(422, "Stage must be between 1 and 6.")
        changes["current_stage"] = payload.stage
        history = enquiry.get("stage_history", [])
        history.append({
            "stage": payload.stage,
            "stage_name": STAGES[payload.stage - 1],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "admin update",
        })
        changes["stage_history"] = history
    updated = update_by_id("enquiries", enquiry_id, changes)
    return updated


@router.get("/stats")
def stats(_admin: bool = Depends(require_admin)):
    enquiries = load("enquiries", [])
    messages = load("messages", [])
    counts = {
        "per_type": {},
        "per_stage": {},
        "per_status": {},
        "total": len(enquiries),
        "unread_replies": sum(
            1 for message in messages if message["direction"] == "in" and message.get("unread")
        ),
        "total_stages_skipped": sum(stages_skipped(item["enquiry_type"]) for item in enquiries),
        "new_today": sum(
            1 for item in enquiries
            if str(item.get("created_at", "")).startswith(datetime.now(timezone.utc).date().isoformat())
        ),
    }
    for item in enquiries:
        counts["per_type"][item["enquiry_type"]] = counts["per_type"].get(item["enquiry_type"], 0) + 1
        stage_name = STAGES[item["current_stage"] - 1]
        counts["per_stage"][stage_name] = counts["per_stage"].get(stage_name, 0) + 1
        counts["per_status"][item["status"]] = counts["per_status"].get(item["status"], 0) + 1
    return counts


@router.post("/seed")
def seed(_admin: bool = Depends(require_admin)):
    return {"loaded": seed_enquiries()}


@router.post("/clear-seed")
def clear(_admin: bool = Depends(require_admin)):
    return {"removed": clear_seed()}


@router.delete("/enquiries/{enquiry_id}")
def delete_enquiry(enquiry_id: str, _admin: bool = Depends(require_admin)):
    enquiries = load("enquiries", [])
    removed = next((item for item in enquiries if item["id"] == enquiry_id), None)
    remaining = [item for item in enquiries if item["id"] != enquiry_id]
    if len(remaining) == len(enquiries):
        raise HTTPException(404, "Enquiry not found.")
    save("enquiries", remaining)
    save("messages", [item for item in load("messages", []) if item["enquiry_id"] != enquiry_id])
    if removed and removed.get("session_id"):
        save("chats", [item for item in load("chats", []) if item["session_id"] != removed["session_id"]])
    return {"removed": enquiry_id}


class AssistRequest(BaseModel):
    instruction: str = ""


@router.post("/enquiries/{enquiry_id}/assist")
def assist_reply(enquiry_id: str, payload: AssistRequest, _admin: bool = Depends(require_admin)):
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry:
        raise HTTPException(404, "Enquiry not found.")
    instruction = payload.instruction.strip() or "Write a polite professional follow-up."
    draft = (
        f"Dear {enquiry['name']},\n\n"
        f"Thank you for your enquiry regarding {', '.join(enquiry.get('product_interest', []))}. "
        f"{instruction}\n\n"
        "Please reply with the application, operating conditions and any specification that may help us assist accurately.\n\n"
        "Kind regards,\nSales Team"
    )
    subject = f"[{enquiry_id}] Re: {', '.join(enquiry.get('product_interest', []))}"
    return {"subject": subject, "body": draft}
