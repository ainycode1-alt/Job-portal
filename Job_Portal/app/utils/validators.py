from __future__ import annotations

import re


def validate_gst(gst: str) -> bool:
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gst))


def validate_phone(phone: str) -> bool:
    pattern = r"^[+]?[0-9]{10,15}$"
    return bool(re.match(pattern, phone))


def validate_url(url: str) -> bool:
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url, re.IGNORECASE))
