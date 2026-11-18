import os
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def require(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "Copy .env.example to .env and set it."
        )
    return value.strip()


COMPANY_NAME = require("COMPANY_NAME", "Sealing Solutions Demo (Prototype Concept)")
ADMIN_PASSWORD = require("ADMIN_PASSWORD", "change_me")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@seallink.local").strip().lower()
SECRET_KEY = require("SECRET_KEY", "change_me_long_random_string")
GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
MAIL_RECIPIENT = os.getenv("MAIL_RECIPIENT", "soumabha015@gmail.com").strip()
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_SSL_PORT = int(os.getenv("SMTP_SSL_PORT", "465"))
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com").strip()
MAIL_POLL_SECONDS = int(os.getenv("MAIL_POLL_SECONDS", "45"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()
SALES_PHONE = os.getenv("SALES_PHONE", "1234567891").strip()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").strip()
