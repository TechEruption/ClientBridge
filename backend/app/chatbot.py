import re
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .config import GEMINI_API_KEY, GEMINI_MODEL, SALES_PHONE
from .knowledge_base import knowledge_text
from .storage import load, save


router = APIRouter(prefix="/api", tags=["chat"])
_rate: dict[str, deque[float]] = defaultdict(deque)
INSTANT_TRIGGERS = ("talk to", "person", "human", "price", "quote", "quotation", "negotiation", "complaint", "urgent", "angry")
SOLVED_TRIGGERS = ("thanks", "thank you", "resolved", "that is all", "that's all", "solved")


class ChatRequest(BaseModel):
    session_id: str
    message: str


def fallback_reply(message: str, count: int) -> str:
    lower = message.lower()
    if any(word in lower for word in ("packing", "ptfe", "gasket")):
        return "We offer industrial sealing products across several categories. Please share the application and operating conditions for a suitable discussion."
    if "industry" in lower or "plant" in lower:
        return "We serve industries including cement, power, steel, chemical, refinery and many others. Tell us your industry and product need."
    if "catalogue" in lower or "catalog" in lower:
        return "A catalogue can be requested through the enquiry form. Our sales team can guide you to the relevant products."
    if "location" in lower or "kolkata" in lower:
        return "The company is based in Kolkata, West Bengal, India."
    return "I can help with product categories, industries, the catalogue and the four enquiry types. Please describe what you need."


@router.post("/chat")
def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not payload.session_id or len(payload.session_id) > 100:
        raise HTTPException(422, "Invalid session id.")
    if not message or len(message) > 500:
        raise HTTPException(422, "Message must be between 1 and 500 characters.")

    now = time.monotonic()
    bucket = _rate[payload.session_id]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= 20:
        raise HTTPException(429, "Please wait before sending another message.")
    bucket.append(now)

    chats = load("chats", [])
    session = next((item for item in chats if item["session_id"] == payload.session_id), None)
    if not session:
        session = {"session_id": payload.session_id, "messages": [], "client_message_count": 0, "number_given": False}
        chats.append(session)

    timestamp = datetime.now(timezone.utc).isoformat()
    session["messages"].append({"role": "client", "content": message, "timestamp": timestamp})
    session["client_message_count"] += 1
    count = session["client_message_count"]
    lower = message.lower()

    instant = any(trigger in lower for trigger in INSTANT_TRIGGERS)
    solved = any(trigger in lower for trigger in SOLVED_TRIGGERS)
    if instant:
        reply = f"Please call our sales team at {SALES_PHONE} for direct assistance."
        session["number_given"] = True
    elif count >= 4:
        if solved:
            reply = "Thank you. We are glad we could help. If you need anything else, our sales team is available at " + SALES_PHONE + "."
        else:
            reply = f"Please speak with our sales team at {SALES_PHONE} so they can assist with your requirement."
        session["number_given"] = True
    else:
        reply = fallback_reply(message, count)

    session["messages"].append({"role": "bot", "content": reply, "timestamp": datetime.now(timezone.utc).isoformat()})
    save("chats", chats)
    return {"reply": reply, "number_given": session["number_given"], "sales_phone": SALES_PHONE}
