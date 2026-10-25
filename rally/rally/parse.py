"""Turn someone's casual private answers into structured preferences.

Claude does the reading when ANTHROPIC_API_KEY is set; a simple keyword parser takes over when it isn't, or when the
API call fails, so the bot always works. Only the answer text is sent to Claude, never names or Discord IDs.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from . import config
from .models import Arrival, Prefs
from .timeparse import on_day, parse_clock, parse_window

log = logging.getLogger("rally.parse")

Diet = Literal["vegetarian", "vegan", "gluten_free", "halal", "kosher", "dairy_free"]


class PrefsOut(BaseModel):
    budget_max: float | None = Field(description="Most they'll spend per person in US dollars, or null if not said")
    diets: list[Diet] = Field(description="Dietary needs that must be respected")
    avoid: list[str] = Field(description="Foods or cuisines they can't or won't eat, short words like 'pork' or 'sushi'")
    free_from: str | None = Field(description="Earliest time they're free, 24-hour HH:MM, or null")
    free_until: str | None = Field(description="Latest time they're free, 24-hour HH:MM, or null")
    under_21: bool = Field(description="True only if they say they're under 21")
    sober: bool = Field(description="True if they don't want a bar or a place built around drinking")
    wants_drinks: bool = Field(description="True if they'd like somewhere that serves alcohol")
    vibe: float | None = Field(description="0 = very chill/quiet, 0.5 = in between, 1 = party/loud; null if not said")
    cravings: list[str] = Field(description="Foods, cuisines or activities they're in the mood for, short words")
    veto: str | None = Field(description="One specific place or cuisine they don't want tonight, or null")


SYSTEM = """You read short, casual messages that college students write privately to a group-planning bot, \
and turn them into structured preferences. Students write loosely ("broke till friday", "lowkey night", \
"no meat", "21+ is fine"). Extract only what they actually said or clearly implied; leave everything else \
null, false or empty. Times are local and usually evening: "free after 7" means free_from 19:00."""


async def parse_prefs(budget: str, diet: str, free: str, drinks_vibe: str, extra: str, day: date | None = None) -> Prefs:
    text = (
        f"Budget: {budget}\nDiet / can't eat: {diet}\nFree time: {free}\n"
        f"Drinks and vibe: {drinks_vibe}\nCravings or veto: {extra}"
    )
    if config.ANTHROPIC_API_KEY:
        try:
            return await _parse_with_claude(text, day)
        except Exception:  # network, refusal, schema; the keyword parser is a safe fallback
            log.exception("Claude parsing failed; using keyword parser")
    return keyword_prefs(budget, diet, free, drinks_vibe, extra, day)


async def _parse_with_claude(text: str, day: date | None) -> Prefs:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
    response = await client.beta.messages.parse(
        model=config.RALLY_MODEL,
        max_tokens=2000,
        system=SYSTEM,
        messages=[{"role": "user", "content": text}],
        output_format=PrefsOut,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise ValueError(f"no parsed output (stop_reason={response.stop_reason})")
    out: PrefsOut = response.parsed_output
    return Prefs(
        budget_max=out.budget_max,
        diets=list(out.diets),
        avoid=[a.lower() for a in out.avoid],
        free_from=on_day(parse_clock(out.free_from or "", evening_default=False), day),
        free_until=on_day(parse_clock(out.free_until or "", evening_default=False), day),
        under_21=out.under_21,
        sober=out.sober,
        wants_drinks=out.wants_drinks and not out.under_21,
        vibe=None if out.vibe is None else max(0.0, min(1.0, out.vibe)),
        cravings=[c.lower() for c in out.cravings],
        veto=out.veto.lower() if out.veto else None,
    )


# ------------------------------------------------------------------ keyword fallback

_DIET_WORDS = {
    "vegan": ["vegan"],
    "vegetarian": ["vegetarian", "veggie", "no meat"],
    "gluten_free": ["gluten", "celiac", "coeliac"],
    "halal": ["halal"],
    "kosher": ["kosher"],
    "dairy_free": ["dairy", "lactose"],
}
_CHILL = ("chill", "lowkey", "low-key", "quiet", "relax", "tired", "cozy", "calm")
_PARTY = ("party", "turn up", "lit", "dance", "dancing", "loud", "rage", "go out", "wild")


def keyword_prefs(budget: str, diet: str, free: str, drinks_vibe: str, extra: str, day: date | None = None) -> Prefs:
    p = Prefs()
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)", budget or "")
    if m:
        p.budget_max = float(m.group(1))
    elif re.search(r"broke|cheap|free", budget or "", re.I):
        p.budget_max = 10.0

    d = (diet or "").lower()
    for key, words in _DIET_WORDS.items():
        if any(w in d for w in words):
            p.diets.append(key)
    if "vegan" in p.diets and "vegetarian" not in p.diets:
        p.diets.append("vegetarian")
    p.avoid = [w.strip() for w in re.findall(r"no ([a-z ]+?)(?:,|\.|$| and )", d) if w.strip() not in ("meat",)]

    p.free_from, p.free_until = parse_window(free or "", day)

    dv = (drinks_vibe or "").lower()
    p.under_21 = bool(re.search(r"under\s*21|not 21|i'?m (1[6-9]|20)\b|\b(18|19|20) ?(yo|y/o)", dv))
    p.sober = any(w in dv for w in ("sober", "no drink", "don't drink", "dont drink", "no alcohol", "no bar"))
    p.wants_drinks = not p.under_21 and not p.sober and any(w in dv for w in ("drinks", "drink", "beer", "bar", "cocktail"))
    chill, party = any(w in dv for w in _CHILL), any(w in dv for w in _PARTY)
    if chill and party:
        p.vibe = 0.5
    elif chill:
        p.vibe = 0.15
    elif party:
        p.vibe = 0.9
    elif "either" in dv or "whatever" in dv or "anything" in dv:
        p.vibe = 0.5

    e = (extra or "").lower()
    veto = re.search(r"(?:veto|not|no|anything but)\s+([a-z0-9' ]+)", e)
    if veto:
        p.veto = veto.group(1).strip()
        e = e.replace(veto.group(0), "")
    p.cravings = [w.strip() for w in re.split(r",| and |/", e) if len(w.strip()) > 2]
    return p


def parse_arrival(rsvp: str, arrive: str, leave: str, other: str, day: date | None = None) -> Arrival:
    """Squad mode answers are short and predictable, so no AI is needed here."""
    earliest = parse_window(arrive, day)[0] if arrive else None
    latest = parse_window("until " + leave, day)[1] if leave else None
    o = (other or "").lower()
    ride = "need" if re.search(r"need (a )?ride|no car|need a lift", o) else "drive" if re.search(r"can drive|i'?ll drive|have a car", o) else None
    return Arrival(rsvp=rsvp, earliest=earliest, latest=latest, ride=ride)
