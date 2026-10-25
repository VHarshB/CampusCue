"""Read event details from a shared link: first the bundled events.json, then the page itself.

Sun Devil Central pages may need an ASU login, in which case the page can't be read and Rally asks whoever shared
the link to fill in the details with the Edit details button.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from html import unescape

import httpx

from .config import DATA_DIR, TZ
from .models import Event

log = logging.getLogger("rally.events")

EVENT_LINK = re.compile(
    r"https?://(?:sundevilcentral\.eoss\.asu\.edu|events\.asu\.edu|asu\.campuslabs\.com|[a-z0-9.-]*asu\.edu/[^\s]*event)[^\s>]*",
    re.I,
)


def find_event_link(text: str) -> str | None:
    m = EVENT_LINK.search(text or "")
    return m.group(0) if m else None


def _load_bundled() -> list[dict]:
    path = DATA_DIR / "events.json"
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("events", [])


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)


def from_dict(d: dict) -> Event:
    return Event(
        title=d.get("title") or "Event",
        url=d.get("url") or "",
        starts_at=_dt(d.get("starts_at")),
        ends_at=_dt(d.get("ends_at")),
        location=d.get("location") or "",
        note=d.get("note") or "",
    )


def _from_json_ld(html: str, url: str) -> Event | None:
    for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for item in items:
            if isinstance(item, dict) and "Event" in str(item.get("@type", "")):
                loc = item.get("location") or {}
                return Event(
                    title=unescape(item.get("name") or "Event"),
                    url=url,
                    starts_at=_dt(item.get("startDate")),
                    ends_at=_dt(item.get("endDate")),
                    location=unescape(loc.get("name", "") if isinstance(loc, dict) else str(loc)),
                )
    return None


def _meta(html: str, prop: str) -> str:
    m = re.search(rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']*)', html, re.I)
    return unescape(m.group(1)).strip() if m else ""


async def lookup(url: str) -> tuple[Event, bool]:
    """Return (event, complete). `complete` is False when the title or start time couldn't be read."""
    for d in _load_bundled():
        if d.get("url") and d["url"].rstrip("/") == url.rstrip("/"):
            ev = from_dict(d)
            return ev, ev.starts_at is not None
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True, headers={"User-Agent": "RallyBot/1.0"}) as client:
            r = await client.get(url)
        html = r.text if r.status_code == 200 else ""
    except httpx.HTTPError:
        log.info("could not fetch %s", url)
        html = ""
    ev = _from_json_ld(html, url) if html else None
    if ev:
        return ev, ev.starts_at is not None
    title = _meta(html, "og:title") if html else ""
    if title and "login" not in title.lower() and "sign in" not in title.lower():
        return Event(title=title, url=url, note=_meta(html, "og:description")[:200]), False
    return Event(title="Shared event", url=url), False
