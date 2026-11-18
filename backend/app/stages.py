STAGES = [
    "Awareness",
    "Client problem",
    "Solve client problem",
    "Discussion",
    "Negotiation",
    "Conversion",
]

TYPE_TO_START_STAGE = {
    "new_client": 1,
    "referral": 4,
    "rebuy": 5,
    "new_product": 3,
}


def stages_skipped(enquiry_type: str) -> int:
    start = TYPE_TO_START_STAGE[enquiry_type]
    return max(0, start - 1)


def stage_history(entry_id: str, timestamp: str, stage: int, reason: str = "initial") -> list[dict]:
    return [{
        "stage": stage,
        "stage_name": STAGES[stage - 1],
        "timestamp": timestamp,
        "reason": reason,
    }]
