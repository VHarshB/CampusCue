from fastapi.testclient import TestClient

from rally.api import create_app
from rally.db import DB
from rally.events import find_event_link


class FakeSharer:
    def __init__(self):
        self.calls = []

    async def share_from_cubbie(self, code, event, shared_by):
        self.calls.append((code, event, shared_by))
        return 123 if code == "ABC123-DEF456" else None


def test_share_endpoint():
    sharer = FakeSharer()
    client = TestClient(create_app(sharer))
    assert client.get("/health").json() == {"ok": True}

    r = client.post("/share", json={"code": "ABC123-DEF456", "title": "Salsa Night", "starts_at": "2026-10-30T19:00:00-07:00", "shared_by": "Maya"})
    assert r.status_code == 200
    code, event, who = sharer.calls[0]
    assert event.title == "Salsa Night" and event.starts_at.hour == 19 and who == "Maya"

    assert client.post("/share", json={"code": "WRONG1-CODE22", "title": "x"}).status_code == 404
    assert client.post("/share", json={"code": "ABC123-DEF456"}).status_code == 400


async def test_db_roundtrip(tmp_path):
    db = DB(str(tmp_path / "t.db"))
    await db.open()
    code = await db.link_code(1, 2)
    assert code == await db.link_code(1, 2)  # stable per channel
    assert (await db.channel_for_code(code.lower()))["channel_id"] == 1

    sid = await db.create_session("decide", 1, 2, 99, question="dinner?", kind="food")
    await db.save_answer(sid, 5, {"budget_max": 10})
    await db.save_answer(sid, 5, {"budget_max": 12})
    assert (await db.answers(sid)) == {5: {"budget_max": 12}}

    await db.vote(sid, 5, 0)
    await db.vote(sid, 5, 1)  # switching replaces the earlier vote
    await db.vote(sid, 5, -1)
    assert await db.tally(sid) == {1: 1, -1: 1}

    await db.unlink(1)
    assert await db.channel_for_code(code) is None
    await db.close()


def test_event_link_detection():
    assert find_event_link("yo check https://sundevilcentral.eoss.asu.edu/rsvp_boot?id=123 tonight")
    assert find_event_link("no links here") is None
