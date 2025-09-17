from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from zoneinfo import ZoneInfo

try:
    from dateutil import parser as _parser  # type: ignore
except Exception:  # pragma: no cover
    _parser = None  # type: ignore


def tz(name: str) -> ZoneInfo:
    """Return a ZoneInfo for an IANA tz database name."""
    return ZoneInfo(name)


def now_utc() -> datetime:
    """Current aware datetime in UTC (tzinfo=UTC)."""
    return datetime.now(timezone.utc)


def now_in(tzname: str, as_utc: bool = True) -> datetime:
    """
    Current time in tzname. If as_utc=True (default), return converted to UTC.
    If as_utc=False, return aware datetime in that tz.
    """
    z = tz(tzname)
    local = datetime.now(z)
    return local.astimezone(timezone.utc) if as_utc else local


def to_utc(dt: Union[datetime, str], tzname: Optional[str] = None) -> datetime:
    """
    Coerce a datetime or string to an aware UTC datetime.

    - If dt is string: parse with dateutil. If tz is missing, tzname must be provided.
    - If dt is naive datetime: tzname must be provided to localize before conversion.
    - If dt is aware: convert to UTC.
    """
    if isinstance(dt, str):
        if _parser is None:
            raise RuntimeError(
                "python-dateutil is required to parse strings. Install with `pip install python-dateutil`."
            )
        parsed = _parser.parse(dt)
        if parsed.tzinfo is None:
            if not tzname:
                raise ValueError(
                    "Naive datetime string; provide tzname to interpret it.")
            parsed = parsed.replace(tzinfo=tz(tzname))
        return parsed.astimezone(timezone.utc)

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            if not tzname:
                raise ValueError(
                    "Naive datetime; provide tzname to interpret it.")
            dt = dt.replace(tzinfo=tz(tzname))
        return dt.astimezone(timezone.utc)

    raise TypeError("dt must be a datetime or string")


def parse_any_to_utc(value: Union[str, datetime], tzname: Optional[str] = None) -> datetime:
    """Alias to to_utc for explicitness."""
    return to_utc(value, tzname=tzname)


def format_dt(dt: datetime, mode: str = "iso") -> str:
    """
    Format an aware datetime. `mode`:
      - 'iso': ISO 8601 with 'Z' if UTC
      - any other string is treated as strftime format
    """
    if dt.tzinfo is None:
        raise ValueError("Datetime must be aware")
    if mode == "iso":
        as_utc = dt.astimezone(timezone.utc)
        return as_utc.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"
    return dt.strftime(mode)


def lima_now_utc() -> datetime:
    """Return 'now' as seen in America/Lima, converted to UTC for storage."""
    return now_in("America/Lima", as_utc=True)


def santiago_now_utc() -> datetime:
    """Return 'now' as seen in America/Santiago, converted to UTC for storage."""
    return now_in("America/Santiago", as_utc=True)
