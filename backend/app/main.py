from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from .config import FRONTEND_ORIGIN
from .storage import load, save
from .routes_public import router as public_router
from .routes_admin import router as admin_router
from .routes_admin_extra import router as admin_extra_router
from .mailer import router as mail_router
from .mail_sync import router as sync_router
from .chatbot import router as chat_router
from .mail_sync import sync_mail
from .config import MAIL_POLL_SECONDS


app = FastAPI(title="ClientBridge Smart Enquiry Portal")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in FRONTEND_ORIGIN.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)
app.include_router(admin_router)
app.include_router(admin_extra_router)
app.include_router(mail_router)
app.include_router(sync_router)
app.include_router(chat_router)


@app.on_event("startup")
def initialize_data() -> None:
    for name in ("enquiries", "messages", "chats"):
        if load(name, None) is None:
            save(name, [])
    if load("sync_state", None) is None:
        save("sync_state", {"last_uid": 0})


def mail_sync_loop() -> None:
    while True:
        sync_mail()
        time.sleep(max(15, MAIL_POLL_SECONDS))


@app.on_event("startup")
def start_mail_sync() -> None:
    thread = threading.Thread(target=mail_sync_loop, daemon=True, name="seallink-mail-sync")
    thread.start()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ClientBridge"}
