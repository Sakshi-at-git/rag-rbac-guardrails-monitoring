import re
from typing import Tuple

from app.config import settings


INJECTION_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"bypass\s+security",
    r"sudo\s+",
]

PII_PATTERNS = [
    (r"\b\d{10}\b", "[REDACTED_PHONE]"),
    (r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED_EMAIL]"),
    (r"\b\d{12}\b", "[REDACTED_ID]"),
]


def validate_query(query: str) -> Tuple[bool, str]:
    if len(query) > settings.max_query_chars:
        return False, f"Query too long. Max allowed is {settings.max_query_chars} chars."

    q = query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, q):
            return False, "Potential prompt injection detected."

    return True, ""


def sanitize_output(text: str) -> str:
    sanitized = text
    for pattern, replacement in PII_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized
