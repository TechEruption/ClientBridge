from .config import COMPANY_NAME, SALES_PHONE


def make_mail(enquiry: dict) -> dict:
    enquiry_id = enquiry["id"]
    name = enquiry["name"]
    company = enquiry["company_name"]
    product = ", ".join(enquiry["product_interest"])
    enquiry_type = enquiry["enquiry_type"]

    if enquiry_type == "new_client":
        subject = f"[{enquiry_id}] Your enquiry about {product}"
        summary = (
            "Fresh lead, start from Awareness. Qualify the need. "
            f"{name} from {company} is interested in {product} for {enquiry['industry']}."
        )
        body = (
            f"Dear {name},\n\n"
            f"Thank you for contacting {COMPANY_NAME}. We would be pleased to understand "
            f"your requirements in {product} and support your {enquiry['industry']} application.\n\n"
            "Please share the application, operating temperature and pressure, and the "
            "current sealing problem you are trying to solve. We can then arrange a relevant catalogue.\n\n"
            "Kind regards,\nSales Team\n"
            f"{COMPANY_NAME}\n{SALES_PHONE}"
        )
    elif enquiry_type == "referral":
        subject = f"[{enquiry_id}] Technical discussion about {product}"
        referrer = enquiry["referred_by"]
        summary = (
            f"Referral from {referrer}. Verify the referrer. Start at Discussion. "
            f"{name} from {company} is interested in {product}."
        )
        body = (
            f"Dear {name},\n\n"
            f"Thank you for contacting {COMPANY_NAME}. We appreciate the referral from {referrer}. "
            "We would be glad to arrange a technical discussion and keep the conversation focused "
            "on the key specifications of your requirement.\n\n"
            "Please share the application, operating conditions and any dimensional or material preferences.\n\n"
            "Kind regards,\nSales Team\n"
            f"{COMPANY_NAME}\n{SALES_PHONE}"
        )
    elif enquiry_type == "rebuy":
        subject = f"[{enquiry_id}] Repeat order enquiry about {product}"
        summary = (
            f"Existing buyer. Pull the previous order {enquiry['previous_order_ref']}. "
            "Go straight to Negotiation, then Conversion."
        )
        body = (
            f"Dear {name},\n\n"
            f"Thank you for continuing to trust {COMPANY_NAME}. We have noted previous order "
            f"{enquiry['previous_order_ref']} and your request for {enquiry['quantity']} units/items "
            f"of {product}.\n\n"
            "We will prepare a quotation for confirmation. Price, delivery time and payment terms "
            "will be confirmed before we proceed.\n\n"
            "Kind regards,\nSales Team\n"
            f"{COMPANY_NAME}\n{SALES_PHONE}"
        )
    else:
        subject = f"[{enquiry_id}] New product requirement: {product}"
        summary = (
            f"Existing customer, new need. Start at Solve client problem. "
            f"The client currently uses {enquiry['current_product_used']} and needs {enquiry['new_product_needed']}."
        )
        body = (
            f"Dear {name},\n\n"
            f"Thank you for approaching {COMPANY_NAME} again. We understand you currently use "
            f"{enquiry['current_product_used']} and are considering {enquiry['new_product_needed']}.\n\n"
            "Please share the application and full specification of the new requirement. "
            "Our team can then propose an appropriate technical recommendation.\n\n"
            "Kind regards,\nSales Team\n"
            f"{COMPANY_NAME}\n{SALES_PHONE}"
        )
    return {"subject": subject, "body": body, "summary": summary}
