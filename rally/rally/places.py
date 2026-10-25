"""The places Decide mode chooses from, loaded from data/places.json."""

from __future__ import annotations

import json
from functools import lru_cache

from .config import DATA_DIR
from .models import Place


@lru_cache(maxsize=1)
def load_places() -> list[Place]:
    raw = json.loads((DATA_DIR / "places.json").read_text())["places"]
    return [Place(**p) for p in raw]
