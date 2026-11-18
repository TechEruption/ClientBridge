import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import require_admin
from .config import GMAIL_USER, GMAIL_APP_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_SSL_PORT
from .storage import load, append


router = APIRouter(prefix="/api/admin", tags=["mail"])


class SendMailRequest(BaseModel):
    subject: str
    body: str
    recipient: str


@router.post("/enquiries/{enquiry_id}/send-mail")
def send_mail(enquiry_id: str, payload: SendMailRequest, _admin: bool = Depends(require_admin)):
    enquiry = next((item for item in load("enquiries", []) if item["id"] == enquiry_id), None)
    if not enquiry:
        raise HTTPException(404, "Enquiry not found.")
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise HTTPException(503, "Gmail SMTP is not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD.")
    if "\r" in payload.subject or "\n" in payload.subject:
        raise HTTPException(422, "Subject contains invalid header characters.")

    outgoing = [item for item in load("messages", []) if item["enquiry_id"] == enquiry_id and item["direction"] == "out"]
    message_id = make_msgid()
    in_reply_to = outgoing[-1]["message_id"] if outgoing else ""
    references = (outgoing[-1].get("references") or outgoing[-1]["message_id"] or "") if outgoing else ""
    if not references:
        references = message_id

    message = EmailMessage()
    message["From"] = GMAIL_USER
    message["To"] = payload.recipient
    message["Subject"] = payload.subject.replace("\r", "").replace("\n", "")
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = message_id
    if outgoing:
        message["In-Reply-To"] = in_reply_to
        message["References"] = references
    message.set_content(payload.body)

    def send_with(starttls: bool) -> None:
        context = ssl.create_default_context()
        if starttls:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                smtp.send_message(message)
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_SSL_PORT, context=context, timeout=20) as smtp:
                smtp.ehlo()
                smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                smtp.send_message(message)

    try:
        send_with(starttls=True)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(502, "Gmail login failed. Check the 16-character Gmail App Password.")
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, TimeoutError, OSError) as first_error:
        try:
            send_with(starttls=False)
        except smtplib.SMTPAuthenticationError:
            raise HTTPException(502, "Gmail login failed. Check the 16-character Gmail App Password.")
        except (smtplib.SMTPException, TimeoutError, OSError) as ssl_error:
            raise HTTPException(
                502,
                "Gmail connection closed unexpectedly on both SMTP ports. "
                "Check the App Password, internet/network filtering, and Gmail access.",
            )

    saved = {
        "id": f"MSG-{len(load('messages', [])) + 1:04d}",
        "enquiry_id": enquiry_id,
        "direction": "out",
        "subject": payload.subject,
        "body": payload.body,
        "recipient": payload.recipient,
        "sender": GMAIL_USER,
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "references": references,
        "attachments": [],
        "unread": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    append("messages", saved)
    return {"sent": True, "message": saved}
