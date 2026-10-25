"""Plain data types shared by the parser, the solver and the bot."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime

DIETS = ("vegetarian", "vegan", "gluten_free", "halal", "kosher", "dairy_free")


@dataclass
class Prefs:
    """One person's private answers for Decide mode. Limits filter options out; preferences rank them."""

    # Limits (must-haves)
    budget_max: float | None = None
    diets: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    free_from: datetime | None = None
    free_until: datetime | None = None
    under_21: bool = False
    sober: bool = False  # doesn't want a place built around drinking
    veto: str | None = None
    # Preferences (nice-to-haves)
    wants_drinks: bool = False
    vibe: float | None = None  # 0 = chill, 1 = party
    cravings: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        d = asdict(self)
        for k in ("free_from", "free_until"):
            d[k] = d[k].isoformat() if d[k] else None
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Prefs":
        d = dict(d)
        for k in ("free_from", "free_until"):
            d[k] = datetime.fromisoformat(d[k]) if d.get(k) else None
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Arrival:
    """One person's answer for Squad mode."""

    rsvp: str = "in"  # in | maybe | out
    earliest: datetime | None = None
    latest: datetime | None = None
    ride: str | None = None  # need | drive | None

    def to_json(self) -> dict:
        return {
            "rsvp": self.rsvp,
            "earliest": self.earliest.isoformat() if self.earliest else None,
            "latest": self.latest.isoformat() if self.latest else None,
            "ride": self.ride,
        }

    @classmethod
    def from_json(cls, d: dict) -> "Arrival":
        return cls(
            rsvp=d.get("rsvp", "in"),
            earliest=datetime.fromisoformat(d["earliest"]) if d.get("earliest") else None,
            latest=datetime.fromisoformat(d["latest"]) if d.get("latest") else None,
            ride=d.get("ride"),
        )


@dataclass
class Place:
    name: str
    kind: str  # food | cafe | activity | bar
    cuisine: list[str]
    price: float  # typical dollars per person
    diets: list[str]
    age_21: bool  # 21+ only
    alcohol: bool  # serves alcohol
    alcohol_focused: bool  # a bar, or drinking is the main point
    vibe: float  # 0 = chill, 1 = party
    walk_min: int  # rough walk from the Memorial Union
    area: str = ""
    link: str = ""


@dataclass
class Event:
    title: str
    url: str = ""
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str = ""
    note: str = ""

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "location": self.location,
            "note": self.note,
        }

    @classmethod
    def from_json(cls, d: dict) -> "Event":
        return cls(
            title=d.get("title") or "Event",
            url=d.get("url") or "",
            starts_at=datetime.fromisoformat(d["starts_at"]) if d.get("starts_at") else None,
            ends_at=datetime.fromisoformat(d["ends_at"]) if d.get("ends_at") else None,
            location=d.get("location") or "",
            note=d.get("note") or "",
        )
