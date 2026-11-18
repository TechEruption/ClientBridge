from datetime import datetime, timezone
from .storage import load, save, append
from .stages import TYPE_TO_START_STAGE, stage_history
from .templates_mail import make_mail


DEMO = [
    ("ENQ-DEMO-0001", "Aarav Sen", "new_client", "Cement Plant", "Compression Packing"),
    ("ENQ-DEMO-0002", "Mira Das", "referral", "Power Plant", "Graphite Sealing Products"),
    ("ENQ-DEMO-0003", "Kabir Roy", "rebuy", "Steel Plant", "Expanded PTFE Products"),
    ("ENQ-DEMO-0004", "Riya Ghosh", "new_product", "Chemical Plant", "Insulation"),
    ("ENQ-DEMO-0005", "Dev Patel", "new_client", "Oil Refinery", "Low Emission Packing"),
    ("ENQ-DEMO-0006", "Sana Khan", "referral", "Valve Manufacturers", "Wiping Pads"),
    ("ENQ-DEMO-0007", "Neel Mukherjee", "rebuy", "Sugar Plant", "Speciality Lubricant"),
    ("ENQ-DEMO-0008", "Isha Banerjee", "new_product", "Pulp & Paper Mill", "Industrial Polymer Products"),
]


def seed_enquiries() -> int:
    current = load("enquiries", [])
    current = [item for item in current if not item.get("illustrative")]
    timestamp = datetime.now(timezone.utc).isoformat()
    count = 0
    for item_id, name, type_name, industry, product in DEMO:
        item = {
            "id": item_id,
            "name": name,
            "designation": "Procurement Manager",
            "phone": "+91 98765 43210",
            "company_email": f"{name.lower().replace(' ', '.')}@example.com",
            "company_name": "Illustrative Company",
            "country": "India",
            "industry": industry,
            "product_interest": [product],
            "enquiry_type": type_name,
            "message": "Illustrative demo requirement.",
            "referred_by": "Illustrative Referrer" if type_name == "referral" else None,
            "previous_order_ref": "INV-DEMO-100" if type_name == "rebuy" else None,
            "quantity": "100 units" if type_name == "rebuy" else None,
            "current_product_used": "Previous sealing product" if type_name == "new_product" else None,
            "new_product_needed": product if type_name == "new_product" else None,
            "session_id": None,
            "created_at": timestamp,
            "status": "new",
            "current_stage": TYPE_TO_START_STAGE[type_name],
            "stage_history": stage_history(item_id, timestamp, TYPE_TO_START_STAGE[type_name], "illustrative seed"),
            "internal_note": "",
            "admin_notes": [],
            "has_unread_reply": False,
            "illustrative": True,
        }
        mail = make_mail(item)
        item["auto_summary"] = mail["summary"]
        item["email_draft"] = {"subject": mail["subject"], "body": mail["body"]}
        current.append(item)
        count += 1
    save("enquiries", current)
    return count


def clear_seed() -> int:
    current = load("enquiries", [])
    remaining = [item for item in current if not item.get("illustrative")]
    removed = len(current) - len(remaining)
    save("enquiries", remaining)
    enquiries = {item["id"] for item in remaining}
    messages = [message for message in load("messages", []) if message.get("enquiry_id") in enquiries]
    save("messages", messages)
    return removed
