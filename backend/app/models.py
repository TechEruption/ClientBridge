from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


EnquiryType = Literal["new_client", "referral", "rebuy", "new_product"]
EnquiryStatus = Literal["new", "in_progress", "closed", "on_hold"]


class EnquiryCreate(BaseModel):
    name: str
    designation: str
    phone: str
    company_email: str
    company_name: str
    country: str
    industry: str
    product_interest: list[str]
    enquiry_type: EnquiryType
    message: str
    referred_by: str | None = None
    previous_order_ref: str | None = None
    quantity: str | None = None
    current_product_used: str | None = None
    new_product_needed: str | None = None
    honeypot: str = ""
    math_answer: str = ""
    session_id: str | None = None


class Enquiry(BaseModel):
    id: str
    name: str
    designation: str
    phone: str
    company_email: str
    company_name: str
    country: str
    industry: str
    product_interest: list[str]
    enquiry_type: EnquiryType
    message: str
    referred_by: str | None = None
    previous_order_ref: str | None = None
    quantity: str | None = None
    current_product_used: str | None = None
    new_product_needed: str | None = None
    session_id: str | None = None
    created_at: str
    status: EnquiryStatus = "new"
    current_stage: int
    stage_history: list[dict[str, Any]]
    internal_note: str = ""
    admin_notes: list[dict[str, Any]] = Field(default_factory=list)
    has_unread_reply: bool = False
    illustrative: bool = False
    auto_summary: str = ""
    email_draft: dict[str, str] = Field(default_factory=dict)


class Message(BaseModel):
    id: str
    enquiry_id: str
    direction: Literal["in", "out"]
    subject: str = ""
    body: str = ""
    recipient: str = ""
    sender: str = ""
    message_id: str = ""
    in_reply_to: str = ""
    references: str = ""
    attachments: list[str] = Field(default_factory=list)
    unread: bool = False
    timestamp: str


class ChatMessage(BaseModel):
    role: Literal["client", "bot"]
    content: str
    timestamp: str


class ChatSession(BaseModel):
    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
    client_message_count: int = 0
    number_given: bool = False
