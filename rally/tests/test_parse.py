from datetime import date

from rally import config
from rally.parse import keyword_prefs, parse_arrival, parse_prefs
from rally.timeparse import parse_clock, parse_when, parse_window

DAY = date(2026, 10, 30)


def test_clock_defaults_to_evening():
    assert parse_clock("7").hour == 19
    assert parse_clock("6:30pm").hour == 18
    assert parse_clock("11am").hour == 11
    assert parse_clock("18:45").minute == 45


def test_windows():
    s, e = parse_window("6-9pm", DAY)
    assert (s.hour, e.hour) == (18, 21)
    s, e = parse_window("after 7", DAY)
    assert s.hour == 19 and e is None
    s, e = parse_window("until 8", DAY)
    assert s is None and e.hour == 20


def test_parse_when():
    assert parse_when("fri 8pm").weekday() == 4
    assert parse_when("10/30 6:30pm").month == 10
    assert parse_when("nonsense") is None


def test_keyword_prefs_limits_and_preferences():
    p = keyword_prefs("broke till friday", "vegan, no pork", "after 7", "under 21, chill night", "tacos, not chipotle", DAY)
    assert p.budget_max == 10
    assert set(p.diets) == {"vegan", "vegetarian"}
    assert "pork" in p.avoid
    assert p.free_from.hour == 19
    assert p.under_21 and not p.wants_drinks
    assert p.vibe < 0.35
    assert p.veto == "chipotle"
    assert "tacos" in p.cravings


def test_keyword_prefs_party():
    p = keyword_prefs("$25", "", "8-11pm", "down to party, drinks", "", DAY)
    assert p.budget_max == 25 and p.vibe > 0.65 and p.wants_drinks and not p.sober


def test_keyword_prefs_sober():
    p = keyword_prefs("", "", "", "sober, chill", "", DAY)
    assert p.sober and not p.wants_drinks


async def test_parse_prefs_without_key_uses_keywords(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    p = await parse_prefs("$15", "halal", "", "either", "", DAY)
    assert p.budget_max == 15 and p.diets == ["halal"] and p.vibe == 0.5


def test_arrival():
    a = parse_arrival("in", "6:30pm", "9pm", "need a ride", DAY)
    assert a.earliest.hour == 18 and a.latest.hour == 21 and a.ride == "need"
    assert parse_arrival("maybe", "", "", "i can drive", DAY).ride == "drive"


async def test_claude_request_and_parsing(monkeypatch):
    """Checks the request Rally sends to Claude and how the structured answer is read, with a fake HTTP transport."""
    import json as _json

    import anthropic
    import httpx2

    sent = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent["body"] = _json.loads(request.content)
        sent["beta"] = request.headers.get("anthropic-beta", "")
        answer = {
            "budget_max": 15, "diets": ["vegetarian"], "avoid": [], "free_from": "19:00", "free_until": None,
            "under_21": True, "sober": False, "wants_drinks": True, "vibe": 0.2, "cravings": ["tacos"], "veto": None,
        }
        return httpx2.Response(200, json={
            "id": "msg_1", "type": "message", "role": "assistant", "model": sent["body"]["model"],
            "content": [{"type": "text", "text": _json.dumps(answer)}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 10},
        })

    real = anthropic.AsyncAnthropic
    monkeypatch.setattr(anthropic, "AsyncAnthropic", lambda api_key: real(api_key=api_key, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))))
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")

    p = await parse_prefs("15 bucks", "veggie", "after 7", "chill, under 21", "tacos", DAY)
    assert p.budget_max == 15 and p.diets == ["vegetarian"] and p.free_from.hour == 19
    assert p.vibe == 0.2  # the value from Claude's answer, not the keyword parser's 0.15
    assert p.under_21 and not p.wants_drinks  # never suggest drinks to someone under 21
    assert sent["body"]["model"] == config.RALLY_MODEL
    assert sent["body"]["output_config"]["format"]["type"] == "json_schema"
    assert sent["body"]["fallbacks"] == "default" and "server-side-fallback-2026-07-01" in sent["beta"]
    assert "Discord" not in _json.dumps(sent["body"]["messages"])  # only the answer text is sent
