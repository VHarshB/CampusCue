"""The decision logic. Plain Python on purpose: no AI here, so every result is predictable and explainable.

Nothing this module returns names a person or repeats anyone's private answer. The group only ever sees
counts ("4 of 5 can make it") and features of the options ("has vegetarian options").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .models import Arrival, Event, Place, Prefs
from .timeparse import hhmm

# ---------------------------------------------------------------- Squad mode


@dataclass
class SquadPlan:
    meet_at: datetime | None
    can_make: int
    going: int  # people who said In or Maybe
    need_ride: int = 0
    can_drive: int = 0

    def summary(self, spot: str) -> str:
        if self.going == 0:
            return "Waiting for people to tap In or Maybe."
        rides = ""
        if self.need_ride or self.can_drive:
            rides = f"\nRides: {self.need_ride} need one, {self.can_drive} can drive."
        if self.meet_at is None:
            return f"{self.going} going so far. Meet at {spot} when the event starts.{rides}"
        everyone = "everyone can make it" if self.can_make == self.going else f"{self.can_make} of {self.going} can make it"
        return f"Meet at {spot}, {hhmm(self.meet_at)} ({everyone}).{rides}"


def squad_suggest(arrivals: list[Arrival], event: Event) -> SquadPlan:
    """Pick the meetup time that the most In/Maybe people can make, as close to the event start as possible."""
    going = [a for a in arrivals if a.rsvp in ("in", "maybe")]
    plan = SquadPlan(
        meet_at=None,
        can_make=0,
        going=len(going),
        need_ride=sum(1 for a in going if a.ride == "need"),
        can_drive=sum(1 for a in going if a.ride == "drive"),
    )
    candidates = {a.earliest for a in going if a.earliest}
    if event.starts_at:
        candidates.add(event.starts_at - timedelta(minutes=10))  # meet a little before it starts
    if event.ends_at:
        candidates = {c for c in candidates if c < event.ends_at}
    if not candidates:
        return plan

    def ok(a: Arrival, t: datetime) -> bool:
        return (a.earliest is None or a.earliest <= t) and (a.latest is None or t < a.latest)

    def rank(t: datetime):
        count = sum(ok(a, t) for a in going)
        gap = abs((t - event.starts_at).total_seconds()) if event.starts_at else t.timestamp()
        return (-count, gap)

    best = min(candidates, key=rank)
    plan.meet_at, plan.can_make = best, sum(ok(a, best) for a in going)
    return plan


# ---------------------------------------------------------------- Decide mode


@dataclass
class Option:
    place: Place
    score: float
    reasons: list[str] = field(default_factory=list)
    misses: int = 0  # how many people's limits it breaks (only nonzero in "closest options" mode)


@dataclass
class DecideResult:
    options: list[Option]
    people: int
    fits_everyone: bool
    time_note: str = ""
    vibe_note: str = ""
    two_part: tuple[Place, Place] | None = None

    def summary(self) -> str:
        lines = [f"{self.people} {'person' if self.people == 1 else 'people'} shared preferences privately."]
        if self.fits_everyone:
            lines.append(f"{len(self.options)} options fit everyone's limits:")
        elif self.options:
            lines.append("Nothing fits everyone's limits, so here are the closest options:")
        else:
            lines.append("I couldn't find anything that works. Try loosening the plan or suggesting a place.")
        if self.time_note:
            lines.append(self.time_note)
        if self.vibe_note:
            lines.append(self.vibe_note)
        return "\n".join(lines)


def _matches(term: str, place: Place) -> bool:
    term = term.lower().strip()
    if not term:
        return False
    hay = " ".join([place.name, *place.cuisine]).lower()
    return term in hay or any(w in hay for w in term.split() if len(w) > 3)


def _breaks_limits(p: Prefs, place: Place) -> bool:
    if p.budget_max is not None and place.price > p.budget_max:
        return True
    if any(d not in place.diets for d in p.diets):
        return True
    if p.under_21 and place.age_21:
        return True
    if p.sober and place.alcohol_focused:
        return True
    if p.veto and _matches(p.veto, place):
        return True
    if any(_matches(a, place) for a in p.avoid):
        return True
    return False


def _kind_ok(kind: str, place: Place) -> bool:
    if kind == "food":
        return place.kind == "food"
    if kind == "activity":
        return place.kind == "activity"
    return True  # "any" or "night"


def _score(group: list[Prefs], place: Place, compromise: bool) -> float:
    s = 0.0
    for p in group:
        if any(_matches(c, place) for c in p.cravings):
            s += 2.0
    vibes = [p.vibe for p in group if p.vibe is not None]
    if vibes:
        s += 3.0 * (1 - sum(abs(v - place.vibe) for v in vibes) / len(vibes))
    if compromise and 0.35 <= place.vibe <= 0.65:
        s += 1.5
    if place.alcohol and not any(p.under_21 for p in group):
        s += 0.5 * sum(p.wants_drinks for p in group)
    s -= place.walk_min / 15
    s -= place.price / 40
    return s


def _reasons(group: list[Prefs], place: Place, compromise: bool) -> list[str]:
    r = []
    if any(p.budget_max is not None for p in group):
        r.append("fits everyone's budget")
    diets = sorted({d for p in group for d in p.diets})
    if diets:
        r.append("has " + " and ".join(d.replace("_", "-") for d in diets) + " options")
    if sum(any(_matches(c, place) for c in p.cravings) for p in group) >= 1:
        r.append("matches what people are craving")
    if compromise and 0.35 <= place.vibe <= 0.65:
        r.append("middle-ground vibe")
    r.append(f"about {place.walk_min} min from the MU")
    return r


def _time_note(group: list[Prefs]) -> str:
    froms = [p.free_from for p in group if p.free_from]
    untils = [p.free_until for p in group if p.free_until]
    if not froms and not untils:
        return ""
    start, end = (max(froms) if froms else None), (min(untils) if untils else None)
    if start and end and start < end:
        return f"Everyone's free {hhmm(start)}–{hhmm(end)}."
    if start and not end:
        return f"Everyone's free from {hhmm(start)}."
    if end and not start:
        return f"Everyone's free until {hhmm(end)}."
    # No shared window: find the start time the most people can make.
    best, best_n = None, 0
    for t in froms:
        n = sum((p.free_from is None or p.free_from <= t) and (p.free_until is None or t < p.free_until) for p in group)
        if n > best_n:
            best, best_n = t, n
    return f"There's no time everyone's free. {best_n} of {len(group)} can do {hhmm(best)}." if best else ""


def decide(group: list[Prefs], places: list[Place], kind: str = "food", top: int = 3) -> DecideResult:
    pool = [pl for pl in places if _kind_ok(kind, pl)]
    vibes = [p.vibe for p in group if p.vibe is not None]
    compromise = len(vibes) >= 2 and max(vibes) - min(vibes) >= 0.5

    fits = [pl for pl in pool if not any(_breaks_limits(p, pl) for p in group)]
    result = DecideResult(options=[], people=len(group), fits_everyone=bool(fits), time_note=_time_note(group))

    if fits:
        ranked = sorted(fits, key=lambda pl: _score(group, pl, compromise), reverse=True)[:top]
        result.options = [Option(pl, _score(group, pl, compromise), _reasons(group, pl, compromise)) for pl in ranked]
    else:
        # Closest options: fewest people whose limits they break. Never say whose.
        scored = sorted(
            pool,
            key=lambda pl: (sum(_breaks_limits(p, pl) for p in group), -_score(group, pl, compromise)),
        )[:2]
        for pl in scored:
            misses = sum(_breaks_limits(p, pl) for p in group)
            result.options.append(
                Option(pl, _score(group, pl, compromise), [f"doesn't fit {misses} {'person' if misses == 1 else 'people'}'s limits"], misses)
            )

    if compromise:
        result.vibe_note = "Vibes are split between chill and party, so middle-ground picks rank higher."
        chill = [pl for pl in fits if pl.vibe <= 0.4 and pl.kind == "food"]
        party_people = [p for p in group if p.vibe is not None and p.vibe >= 0.6]
        party = [
            pl for pl in places
            if pl.vibe >= 0.7 and pl.kind != "food" and not any(_breaks_limits(p, pl) for p in party_people)
        ]
        if chill and party:
            first = max(chill, key=lambda pl: _score(group, pl, False))
            second = max(party, key=lambda pl: _score(party_people, pl, False))
            result.two_part = (first, second)
            result.vibe_note += f"\nOr make it a two-part night: {first.name} together first, then {second.name} for whoever's still in."
    return result
