PRODUCT_CATEGORIES = [
    "Compression Packing", "Expanded PTFE Products", "Industrial Polymer Products",
    "Insulation", "Graphite Sealing Products", "Speciality Lubricant",
    "Low Emission Packing", "Automotive DPF Gaskets", "Wiping Pads",
]

INDUSTRIES = [
    "Breweries Bottling & Distilleries", "Cement Plant", "Chemical Plant",
    "Fertilisers", "Food Processing Industry", "Mines", "Oil Refinery",
    "Paint Manufacturing Plant", "Petrochemical Plant", "Power Plant",
    "Pulp & Paper Mill", "Steel Plant", "Sugar Plant", "Valve Manufacturers",
]


def knowledge_text(company_name: str, phone: str) -> str:
    return f"""
Company: {company_name}
Location: Kolkata, West Bengal, India
Sales phone: {phone}
Product categories: {", ".join(PRODUCT_CATEGORIES)}.
Industries served: {", ".join(INDUSTRIES)}.
The public enquiry form offers four enquiry types:
new_client: first-time customer, starts at Awareness;
referral: referred customer, starts at Discussion;
rebuy: repeat order, starts at Negotiation;
new_product: existing customer with a new product need, starts at Solve client problem.
The catalogue can be requested through the enquiry form.
Never state prices, discounts, delivery dates, stock availability, certifications or technical specifications.
"""
