"""Turn casual times like "6:30pm", "18:30", "after 7" or "6-9pm" into datetimes in Arizona time."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta

from .config import TZ

_TIME = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|a|p)?\b", re.I)
_RANGE = re.compile(
    r"(\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)\s*(?:-|–|to|until|till)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)",
    re.I,
)


def now() -> datetime:
    return datetime.now(TZ)


def parse_clock(text: str, evening_default: bool = True) -> time | None:
    """Parse one clock time. Without am/pm, 1-11 is read as evening (students plan nights)."""
    if not text:
        return None
    text = text.strip().lower()
    if text in ("noon", "midday"):
        return time(12, 0)
    if text == "midnight":
        return time(23, 59)
    m = _TIME.search(text)
    if not m:
        return None
    hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if hour > 23 or minute > 59:
        return None
    if ampm.startswith("p") and hour < 12:
        hour += 12
    elif ampm.startswith("a") and hour == 12:
        hour = 0
    elif not ampm and evening_default and 1 <= hour <= 11:
        hour += 12
    return time(hour, minute)


def on_day(t: time | None, day: date | None = None) -> datetime | None:
    if t is None:
        return None
    day = day or now().date()
    return datetime.combine(day, t, tzinfo=TZ)


def parse_window(text: str, day: date | None = None) -> tuple[datetime | None, datetime | None]:
    """Parse a free-time window. "6-9pm" -> (18:00, 21:00); "after 7" -> (19:00, None); "until 8" -> (None, 20:00)."""
    if not text:
        return None, None
    low = text.lower()
    m = _RANGE.search(low)
    if m:
        a, b = m.group(1), m.group(2)
        # "6-9pm": the am/pm on the second time applies to the first one too.
        suffix = re.search(r"(am|pm|a|p)\s*$", b)
        if suffix and not re.search(r"(am|pm|a|p)\s*$", a):
            a = a + suffix.group(1)
        start, end = on_day(parse_clock(a), day), on_day(parse_clock(b), day)
        if start and end and end <= start:
            end += timedelta(days=1)
        return start, end
    if any(w in low for w in ("until", "till", "before", "by ")):
        return None, on_day(parse_clock(low), day)
    if "now" in low or "anytime" in low or "any time" in low or "whenever" in low:
        return now(), None
    return on_day(parse_clock(low), day), None


_WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def parse_when(text: str) -> datetime | None:
    """Parse "7pm", "today 7pm", "tomorrow 6:30pm", "fri 8pm" or "10/30 7pm" into a datetime."""
    if not text:
        return None
    low = text.lower()
    day = now().date()
    if "tomorrow" in low or "tmrw" in low:
        day += timedelta(days=1)
        low = low.replace("tomorrow", "").replace("tmrw", "")
    else:
        md = re.search(r"\b(\d{1,2})/(\d{1,2})\b", low)
        if md:
            month, dom = int(md.group(1)), int(md.group(2))
            try:
                day = date(day.year, month, dom)
            except ValueError:
                return None
            if day < now().date():
                day = date(day.year + 1, month, dom)
            low = low.replace(md.group(0), "")
        else:
            for i, wd in enumerate(_WEEKDAYS):
                if re.search(rf"\b{wd}", low):
                    day += timedelta(days=(i - day.weekday()) % 7)
                    break
    return on_day(parse_clock(low), day)


def hhmm(dt: datetime | None) -> str:
    if dt is None:
        return "?"
    return dt.strftime("%-I:%M %p").replace(":00 ", " ").lower()
