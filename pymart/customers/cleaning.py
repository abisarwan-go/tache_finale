"""Normalize messy PyMart customer records (name, email, phone)."""

from __future__ import annotations

import re

INVALID = "INVALID"

# Optional tighter check; string-method validation remains the default.
_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def split_record(raw: str) -> tuple[str, str, str]:
    """Split a pipe-delimited record into name, email, phone (stripped)."""
    parts = [part.strip() for part in raw.split("|")]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]


def clean_name(name: str) -> str:
    """Trim, collapse internal spaces, and apply title case."""
    collapsed = " ".join(name.split())
    if not collapsed:
        return INVALID
    return collapsed.title()


def is_valid_email(email: str, *, use_regex: bool = False) -> bool:
    """Validate email with string methods (default) or optional regex."""
    if use_regex:
        return bool(_EMAIL_REGEX.fullmatch(email))

    if " " in email or email.count("@") != 1:
        return False
    if email.startswith("@") or email.endswith("@"):
        return False

    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False
    return True


def clean_email(email: str, *, use_regex: bool = False) -> str:
    """Trim, remove internal spaces, lowercase; INVALID if format fails."""
    normalized = "".join(email.split()).lower()
    if not is_valid_email(normalized, use_regex=use_regex):
        return INVALID
    return normalized


def clean_phone(phone: str) -> str:
    """Keep digits only and format as (XXX) XXX-XXXX for US numbers."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return INVALID
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def normalize_record(raw: str, *, use_regex_email: bool = False) -> dict[str, str]:
    """Return a standardized customer dict from one raw record string."""
    name, email, phone = split_record(raw)
    return {
        "name": clean_name(name),
        "email": clean_email(email, use_regex=use_regex_email),
        "phone": clean_phone(phone),
    }
