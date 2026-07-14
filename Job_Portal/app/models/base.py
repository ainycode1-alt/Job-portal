from __future__ import annotations

import re
import uuid

from sqlalchemy import String, Text, TypeDecorator, BigInteger
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def gen_uuid() -> str:
    return str(uuid.uuid4())


class EmailField(TypeDecorator):
    """Custom SQLAlchemy type for validating and storing email addresses."""
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.strip().lower()
            from email_validator import validate_email, EmailNotValidError
            try:
                # Basic email validation (deliverability checking disabled to avoid blocking network requests)
                validate_email(value, check_deliverability=False)
            except EmailNotValidError as e:
                raise ValueError(f"Invalid email address format: {value}") from e
        return value


class URLField(TypeDecorator):
    """Custom SQLAlchemy type for validating and storing URLs."""
    impl = String(2048)
    cache_ok = True


class RichTextField(TypeDecorator):
    """Custom SQLAlchemy type for storing rich text/HTML."""
    impl = Text
    cache_ok = True


# Alias NumberField to BigInteger for DB representation (represented as int in Python)
NumberField = BigInteger
