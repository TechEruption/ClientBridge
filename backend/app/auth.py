import base64
import hashlib
import hmac
import time
from fastapi import Header, HTTPException
from .config import ADMIN_PASSWORD, SECRET_KEY


def login(password: str) -> str:
    if not hmac.compare_digest(password, ADMIN_PASSWORD):
        raise HTTPException(401, "Invalid password.")
    expires = int(time.time()) + 8 * 60 * 60
    payload = base64.urlsafe_b64encode(str(expires).encode()).decode().rstrip("=")
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def require_admin(authorization: str | None = Header(default=None)) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Admin authentication required.")
    token = authorization[7:]
    try:
        payload, signature = token.rsplit(".", 1)
    except ValueError:
        raise HTTPException(401, "Invalid session token.")
    expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(401, "Invalid session token.")
    padded = payload + "=" * (-len(payload) % 4)
    expires = int(base64.urlsafe_b64decode(padded).decode())
    if expires < int(time.time()):
        raise HTTPException(401, "Session has expired.")
    return True
