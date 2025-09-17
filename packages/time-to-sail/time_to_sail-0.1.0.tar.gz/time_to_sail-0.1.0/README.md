# time-to-sail

UTC-first datetime utilities for Python apps and ORMs.

- Always store **timezone-aware UTC** datetimes.
- Parse strings in many formats (via `python-dateutil`) and coerce to UTC.
- Convert for display using IANA zones (`zoneinfo`).
- SQLAlchemy helpers to **force UTC** on write/read.

## Quickstart

```python
from timetosail import now_utc, to_utc, now_in
from timetosail.sqlalchemy import UTCDateTime, utc_now

dt = now_utc()  # aware UTC
to_utc("2025-09-16 08:30", tzname="America/Lima")
```
## SQLAlchemy

```python
from sqlalchemy.orm import Mapped, mapped_column
from timetosail.sqlalchemy import UTCDateTime, utc_now

fecha_creacion: Mapped[datetime] = mapped_column(
    UTCDateTime(timezone=True), default=utc_now, nullable=False
)
```

## Install Manual

```bash
pip install -e .
```

## Build & Publish

```bash
pip install build twine
python -m build
python -m twine upload dist/*
```
