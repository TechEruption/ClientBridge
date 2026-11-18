import html
import re
import time
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from collections import defaultdict, deque
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .models import EnquiryCreate
from .storage import load, append, next_sequential_id
from .stages import TYPE_TO_START_STAGE, stage_history
from .templates_mail import make_mail
from .knowledge_base import PRODUCT_CATEGORIES, INDUSTRIES
from .config import GMAIL_USER, GMAIL_APP_PASSWORD, SMTP_HOST, SMTP_PORT, MAIL_RECIPIENT
from .storage import load, append, update_by_id


router = APIRouter(prefix="/api", tags=["public"])
_rate: dict[str, deque[float]] = defaultdict(deque)


NAME_RE = re.compile(r"^[A-Za-z\s\-']+$")
PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_text(value: str) -> str:
    return html.escape(value.strip(), quote=True)


@router.get("/client/enquiries")
def client_enquiries(email: str):
    email = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(422, "Enter a valid email.")
    items = [
        item for item in load("enquiries", [])
        if str(item.get("company_email", "")).lower() == email
    ]
    return items


@router.get("/client/enquiries/{enquiry_id}")
def client_enquiry_detail(enquiry_id: str, email: str):
    email = email.strip().lower()
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry or str(enquiry.get("company_email", "")).lower() != email:
        raise HTTPException(404, "Enquiry not found.")
    messages = [
        item for item in load("messages", [])
        if item["enquiry_id"] == enquiry_id
    ]
    return {**enquiry, "messages": sorted(messages, key=lambda item: item["timestamp"])}


class ClientReply(BaseModel):
    email: str
    body: str


@router.post("/client/enquiries/{enquiry_id}/reply")
def client_reply(enquiry_id: str, payload: ClientReply):
    email = payload.email.strip().lower()
    body = payload.body.strip()
    if len(body) > 5000:
        raise HTTPException(422, "Reply is too long.")
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry or str(enquiry.get("company_email", "")).lower() != email:
        raise HTTPException(404, "Enquiry not found.")
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise HTTPException(503, "Gmail SMTP is not configured.")

    outgoing = [
        item for item in load("messages", [])
        if item["enquiry_id"] == enquiry_id and item["direction"] == "out"
    ]
    subject = f"[{enquiry_id}] Re: {', '.join(enquiry.get('product_interest', []))}"
    message_id = make_msgid()
    in_reply_to = outgoing[-1]["message_id"] if outgoing else ""
    references = (outgoing[-1].get("references") or outgoing[-1].get("message_id") or "") if outgoing else ""

    message = EmailMessage()
    message["From"] = email
    message["To"] = GMAIL_USER or MAIL_RECIPIENT
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = message_id
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = references
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(message)
    except (smtplib.SMTPException, TimeoutError, OSError) as exc:
        raise HTTPException(502, f"Could not send email: {exc}")

    append("messages", {
        "id": f"MSG-{len(load('messages', [])) + 1:04d}",
        "enquiry_id": enquiry_id,
        "direction": "in",
        "subject": subject,
        "body": body,
        "recipient": GMAIL_USER,
        "sender": email,
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "references": references,
        "attachments": [],
        "unread": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    update_by_id("enquiries", enquiry_id, {"has_unread_reply": True})
    return {"sent": True}


@router.get("/catalogue/options")
def catalogue_options():
    return {"products": PRODUCT_CATEGORIES, "industries": INDUSTRIES}


@router.post("/enquiries")
async def create_enquiry(payload: EnquiryCreate, request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = _rate[ip]
    while bucket and now - bucket[0] > 600:
        bucket.popleft()
    if len(bucket) >= 10:
        raise HTTPException(429, "Too many enquiries. Please try again later.")

    if payload.honeypot:
        raise HTTPException(400, "Spam detected.")
    if payload.math_answer.strip() != "7":
        raise HTTPException(422, "Please answer the security question correctly.")

    if not payload.name or not NAME_RE.match(payload.name):
        raise HTTPException(422, "Name may contain only letters, spaces, hyphens and apostrophes.")
    if not payload.designation or not NAME_RE.match(payload.designation):
        raise HTTPException(422, "Designation may contain only letters, spaces, hyphens and apostrophes.")
    if not PHONE_RE.match(payload.phone):
        raise HTTPException(422, "Phone must include a country code, for example +919876543210.")
    if not EMAIL_RE.match(payload.company_email):
        raise HTTPException(422, "Please enter a valid company email.")
    if payload.industry not in INDUSTRIES:
        raise HTTPException(422, "Please choose a valid industry.")
    if not payload.product_interest or any(p not in PRODUCT_CATEGORIES for p in payload.product_interest):
        raise HTTPException(422, "Please choose valid product categories.")
    if not payload.message.strip():
        raise HTTPException(422, "Message cannot be blank.")

    if payload.enquiry_type == "referral" and not payload.referred_by:
        raise HTTPException(422, "Referred by is required.")
    if payload.enquiry_type == "rebuy" and (not payload.previous_order_ref or not payload.quantity):
        raise HTTPException(422, "Previous order reference and quantity are required.")
    if payload.enquiry_type == "new_product" and (
        not payload.current_product_used or not payload.new_product_needed
    ):
        raise HTTPException(422, "Current product and new product needed are required.")

    bucket.append(now)
    enquiry_id = next_sequential_id("enquiries", "ENQ-")
    timestamp = datetime.now(timezone.utc).isoformat()
    stage = TYPE_TO_START_STAGE[payload.enquiry_type]
    data = payload.model_dump()
    for key in (
        "name", "designation", "phone", "company_email", "company_name", "country",
        "industry", "message", "referred_by", "previous_order_ref", "quantity",
        "current_product_used", "new_product_needed", "session_id",
    ):
        if isinstance(data.get(key), str):
            data[key] = clean_text(data[key])

    enquiry = {
        **data,
        "honeypot": "",
        "math_answer": "",
        "id": enquiry_id,
        "created_at": timestamp,
        "status": "new",
        "current_stage": stage,
        "stage_history": stage_history(enquiry_id, timestamp, stage),
        "internal_note": "",
        "admin_notes": [],
        "has_unread_reply": False,
        "illustrative": False,
    }
    mail = make_mail(enquiry)
    enquiry["auto_summary"] = mail["summary"]
    enquiry["email_draft"] = {"subject": mail["subject"], "body": mail["body"]}

    if payload.session_id:
        chats = load("chats", [])
        session = next((chat for chat in chats if chat.get("session_id") == payload.session_id), None)
        if session:
            enquiry["chat_transcript"] = session

    append("enquiries", enquiry)
    return {"thank_you": "Thank you for your enquiry.", "enquiry_id": enquiry_id}
