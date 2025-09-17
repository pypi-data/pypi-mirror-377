from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.types import TypeDecorator, DateTime
from sqlalchemy import text

from .core import to_utc, now_utc


class UTCDateTime(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that guarantees UTC-aware datetimes.

    - On bind: any datetime/string is coerced to aware UTC.
    - On result: returned datetime is set to UTC tzinfo.

    Use with DateTime(timezone=True).
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Any:
        if value is None:
            return None
        if isinstance(value, (str, datetime)):
            value = to_utc(value)
        elif not isinstance(value, datetime):
            raise TypeError(
                "UTCDateTime only accepts datetime or string values.")
        if value.tzinfo is None:
            raise ValueError(
                "Naive datetime not allowed. Provide tz or use to_utc(..., tzname=...).")
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def utc_now() -> datetime:
    """Convenience wrapper for SQLAlchemy defaults."""
    return now_utc()


POSTGRES_UTC_NOW = text("timezone('utc', now())")
