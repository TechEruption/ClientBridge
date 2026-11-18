import html
import imaplib
import re
import email
from email.header import decode_header, make_header
from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from .auth import require_admin
from .config import GMAIL_USER, GMAIL_APP_PASSWORD, IMAP_HOST
from .storage import load, save, append, update_by_id


router = APIRouter(prefix="/api/admin", tags=["mail-sync"])


def decode_header_value(value: str) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def strip_reply(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            continue
        if re.match(r"^On\s.+\s(wrote|said):", stripped, re.I):
            break
        if re.match(r"^(-{2,}|_{2,}|sent from my)", stripped, re.I):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def plain_text(message) -> str:
    if message.is_multipart():
        plain = None
        html_part = None
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            subtype = part.get_content_subtype()
            try:
                decoded = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
            except Exception:
                continue
            if subtype == "plain" and plain is None:
                plain = decoded
            elif subtype == "html" and html_part is None:
                html_part = decoded
        text = plain or html_part or ""
    else:
        text = message.get_payload(decode=True)
        text = text.decode(message.get_content_charset() or "utf-8", "replace") if isinstance(text, bytes) else str(text)
    if "<" in text and ">" in text:
        text = re.sub(r"<(br|p|div)[^>]*>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
    return strip_reply(text)


def sync_mail() -> dict:
    state = load("sync_state", {})
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return {"synced": 0, "error": "Gmail login not configured."}
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("INBOX")
    except (imaplib.IMAP4.error, OSError) as exc:
        return {"synced": 0, "error": f"Gmail login failed: {exc}"}

    last_uid = int(state.get("last_uid", 0))
    typ, data = mail.uid("search", None, "ALL")
    if typ != "OK":
        mail.logout()
        return {"synced": 0, "error": "Could not search Gmail."}
    uids = data[0].split()
    processed = last_uid
    imported = 0
    outgoing = load("messages", [])
    outgoing_ids = {item.get("message_id") for item in outgoing if item.get("direction") == "out"}
    enquiries = load("enquiries", [])

    for raw_uid in uids:
        uid = int(raw_uid)
        if uid <= last_uid:
            continue
        typ, raw = mail.uid("fetch", raw_uid, "(RFC822)")
        if typ != "OK" or not raw or not raw[0]:
            processed = max(processed, uid)
            continue
        message = email.message_from_bytes(raw[0][1])
        message_id = message.get("Message-ID", "").strip()
        if message_id in outgoing_ids:
            processed = max(processed, uid)
            continue
        references = (message.get("In-Reply-To") or "") + " " + (message.get("References") or "")
        enquiry = None
        for out in outgoing:
            if out.get("direction") == "out" and out.get("message_id") in references:
                enquiry = next((item for item in enquiries if item["id"] == out["enquiry_id"]), None)
                break
        if not enquiry:
            match = re.search(r"\[(ENQ-\d{4}(?:-[A-Z0-9]+)?|ENQ-DEMO-\d{4})\]", decode_header_value(message.get("Subject", "")))
            if match:
                enquiry = next((item for item in enquiries if item["id"] == match.group(1)), None)
        if not enquiry:
            sender = decode_header_value(message.get("From", ""))
            sender_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", sender)
            if sender_match:
                sender_email = sender_match.group(0).lower()
                matches = [
                    item for item in enquiries
                    if str(item.get("company_email", "")).lower() == sender_email
                ]
                if len(matches) == 1:
                    enquiry = matches[0]
        if enquiry:
            attachment_names = [
                part.get_filename() for part in message.walk()
                if part.get_filename()
            ]
            saved = {
                "id": f"MSG-{len(load('messages', [])) + 1:04d}",
                "enquiry_id": enquiry["id"],
                "direction": "in",
                "subject": decode_header_value(message.get("Subject", "")),
                "body": plain_text(message),
                "recipient": GMAIL_USER,
                "sender": decode_header_value(message.get("From", "")),
                "message_id": message_id,
                "in_reply_to": message.get("In-Reply-To", ""),
                "references": message.get("References", ""),
                "attachments": attachment_names,
                "unread": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            append("messages", saved)
            update_by_id("enquiries", enquiry["id"], {"has_unread_reply": True})
            outgoing = load("messages", [])
            imported += 1
        processed = max(processed, uid)

    save("sync_state", {"last_uid": processed, "last_synced": datetime.now(timezone.utc).isoformat()})
    mail.logout()
    return {"synced": imported, "last_uid": processed}


@router.post("/sync-now")
def sync_now(_admin: bool = Depends(require_admin)):
    return sync_mail()
