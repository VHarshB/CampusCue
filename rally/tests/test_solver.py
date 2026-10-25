from datetime import datetime, timedelta

from rally.config import TZ
from rally.models import Arrival, Event, Place, Prefs
from rally.places import load_places
from rally.solver import decide, squad_suggest

DAY = datetime(2026, 10, 30, tzinfo=TZ)


def at(h, m=0):
    return DAY.replace(hour=h, minute=m)


def place(name, **kw):
    base = dict(kind="food", cuisine=[], price=12, diets=[], age_21=False, alcohol=False, alcohol_focused=False, vibe=0.3, walk_min=10)
    base.update(kw)
    return Place(name=name, **base)


# ---------------------------------------------------------------- squad


def test_squad_picks_time_most_people_can_make():
    event = Event(title="Salsa Night", starts_at=at(19), ends_at=at(21))
    arrivals = [Arrival("in", at(18, 30), latest=at(19, 15)), Arrival("in", at(18, 50)), Arrival("maybe", at(19, 30)), Arrival("out")]
    plan = squad_suggest(arrivals, event)
    assert plan.going == 3
    assert plan.meet_at == at(18, 50)
    assert plan.can_make == 2
    assert "2 of 3 can make it" in plan.summary("the MU")


def test_squad_everyone_and_rides():
    event = Event(title="Show", starts_at=at(20))
    arrivals = [Arrival("in", at(19), ride="need"), Arrival("in", at(19, 30), ride="drive")]
    plan = squad_suggest(arrivals, event)
    assert plan.can_make == 2
    assert "everyone can make it" in plan.summary("the door")
    assert "1 need one, 1 can drive" in plan.summary("the door")


def test_squad_respects_leave_time():
    event = Event(title="Show", starts_at=at(20))
    arrivals = [Arrival("in", at(18), latest=at(19)), Arrival("in", at(18, 30))]
    plan = squad_suggest(arrivals, event)
    assert plan.meet_at == at(18, 30) and plan.can_make == 2


def test_squad_no_answers():
    assert squad_suggest([], Event(title="x")).summary("there").startswith("Waiting")


# ---------------------------------------------------------------- decide


def test_hard_limits_filter_quietly():
    places = [
        place("Cheap Veg", price=10, diets=["vegetarian"]),
        place("Pricey Veg", price=30, diets=["vegetarian"]),
        place("Cheap Meat", price=8),
        place("Club", kind="food", age_21=True, alcohol=True, alcohol_focused=True, diets=["vegetarian"], price=5),
    ]
    group = [Prefs(budget_max=15), Prefs(diets=["vegetarian"]), Prefs(under_21=True)]
    result = decide(group, places)
    names = [o.place.name for o in result.options]
    assert names == ["Cheap Veg"]
    assert result.fits_everyone
    # The group summary never mentions age or alcohol, and never names anyone.
    text = result.summary() + " ".join(r for o in result.options for r in o.reasons)
    assert "21" not in text and "alcohol" not in text.lower()


def test_veto_and_sober():
    places = [place("Chipotle"), place("Taco Bar", alcohol=True, alcohol_focused=True), place("Pho House")]
    group = [Prefs(veto="chipotle"), Prefs(sober=True)]
    assert [o.place.name for o in decide(group, places).options] == ["Pho House"]


def test_cravings_rank_higher():
    places = [place("Burger Barn", cuisine=["burgers"]), place("Taco Town", cuisine=["tacos", "mexican"])]
    group = [Prefs(cravings=["tacos"]), Prefs(cravings=["mexican"])]
    assert decide(group, places).options[0].place.name == "Taco Town"


def test_chill_vs_party_compromise_and_two_part():
    places = [
        place("Quiet Cafe", vibe=0.1),
        place("Bowling", kind="activity", vibe=0.5),
        place("Middle Grill", vibe=0.5),
        place("Dance Club", kind="bar", vibe=0.95, age_21=True, alcohol=True, alcohol_focused=True),
    ]
    group = [Prefs(vibe=0.1), Prefs(vibe=0.95, wants_drinks=True)]
    result = decide(group, places, kind="food")
    assert result.options[0].place.name == "Middle Grill"
    assert "middle-ground vibe" in result.options[0].reasons
    assert result.two_part == (places[0], places[3])
    assert "two-part night" in result.vibe_note


def test_two_part_skips_party_place_for_under_21_partier():
    places = [place("Quiet Cafe", vibe=0.1), place("Dance Club", kind="bar", vibe=0.95, age_21=True)]
    group = [Prefs(vibe=0.1), Prefs(vibe=0.95, under_21=True)]
    assert decide(group, places).two_part is None


def test_nothing_fits_gives_closest_without_names():
    places = [place("A", price=20), place("B", price=25)]
    group = [Prefs(budget_max=10), Prefs()]
    result = decide(group, places)
    assert not result.fits_everyone
    assert result.options[0].misses == 1
    assert "doesn't fit 1 person's limits" in result.options[0].reasons[0]


def test_shared_free_window():
    group = [Prefs(free_from=at(18), free_until=at(22)), Prefs(free_from=at(19), free_until=at(21))]
    assert decide(group, [place("A")]).time_note == "Everyone's free 7 pm–9 pm."


def test_no_shared_window_reports_best_time():
    group = [Prefs(free_from=at(17), free_until=at(18)), Prefs(free_from=at(19)), Prefs(free_from=at(19, 30))]
    note = decide(group, [place("A")]).time_note
    assert "no time everyone's free" in note and "2 of 3" in note


def test_bundled_places_load_and_work():
    places = load_places()
    assert len(places) >= 20
    result = decide([Prefs(budget_max=15, diets=["vegan"], vibe=0.2)], places)
    assert result.fits_everyone and len(result.options) == 3
    assert all(o.place.price <= 15 and "vegan" in o.place.diets for o in result.options)
