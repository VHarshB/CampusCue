"""SQLite storage. Private answers live only in the `answers` table and are deleted after the plan is over."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta

import aiosqlite

from . import config
from .timeparse import now

SCHEMA = """
CREATE TABLE IF NOT EXISTS groups (
    channel_id INTEGER PRIMARY KEY,
    guild_id   INTEGER NOT NULL,
    link_code  TEXT UNIQUE,
    paused     INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id  INTEGER NOT NULL,
    guild_id    INTEGER NOT NULL,
    mode        TEXT NOT NULL,              -- squad | decide
    starter_id  INTEGER,
    status      TEXT NOT NULL DEFAULT 'open', -- open | voting | locked | closed
    event_json  TEXT,                       -- squad: the event
    question    TEXT,                       -- decide: what the group is deciding
    kind        TEXT,                       -- decide: food | activity | any
    options_json TEXT,                      -- decide: the shortlist being voted on
    plan_json   TEXT,                       -- the locked plan
    message_id  INTEGER,                    -- the card Rally keeps editing
    pick_at     TEXT,                       -- decide: when to pick automatically
    plan_at     TEXT,                       -- when the plan happens
    reminded    INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS answers (
    session_id INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    data_json  TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (session_id, user_id)
);
CREATE TABLE IF NOT EXISTS votes (
    session_id INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    choice     INTEGER NOT NULL,             -- option index, or -1 for a Lock it in vote
    PRIMARY KEY (session_id, user_id, choice)
);
"""


class DB:
    def __init__(self, path: str | None = None):
        self.path = path or config.DB_PATH
        self.conn: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    async def _one(self, sql: str, *args):
        async with self.conn.execute(sql, args) as cur:
            return await cur.fetchone()

    async def _all(self, sql: str, *args):
        async with self.conn.execute(sql, args) as cur:
            return await cur.fetchall()

    async def _run(self, sql: str, *args) -> int:
        cur = await self.conn.execute(sql, args)
        await self.conn.commit()
        return cur.lastrowid

    # ---- groups and Cubbie link codes

    async def link_code(self, channel_id: int, guild_id: int) -> str:
        row = await self._one("SELECT link_code FROM groups WHERE channel_id = ?", channel_id)
        if row and row["link_code"]:
            return row["link_code"]
        code = f"{secrets.token_hex(3).upper()}-{secrets.token_hex(3).upper()}"
        await self._run(
            "INSERT INTO groups (channel_id, guild_id, link_code, created_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(channel_id) DO UPDATE SET link_code = excluded.link_code",
            channel_id, guild_id, code, now().isoformat(),
        )
        return code

    async def unlink(self, channel_id: int) -> None:
        await self._run("UPDATE groups SET link_code = NULL WHERE channel_id = ?", channel_id)

    async def channel_for_code(self, code: str):
        return await self._one("SELECT channel_id, guild_id, paused FROM groups WHERE link_code = ?", code.strip().upper())

    async def set_paused(self, channel_id: int, guild_id: int, paused: bool) -> None:
        await self._run(
            "INSERT INTO groups (channel_id, guild_id, paused, created_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(channel_id) DO UPDATE SET paused = excluded.paused",
            channel_id, guild_id, int(paused), now().isoformat(),
        )

    async def is_paused(self, channel_id: int) -> bool:
        row = await self._one("SELECT paused FROM groups WHERE channel_id = ?", channel_id)
        return bool(row and row["paused"])

    # ---- sessions

    async def create_session(self, mode: str, channel_id: int, guild_id: int, starter_id: int | None, **fields) -> int:
        cols = ["mode", "channel_id", "guild_id", "starter_id", "created_at", *fields]
        vals = [mode, channel_id, guild_id, starter_id, now().isoformat(), *fields.values()]
        return await self._run(
            f"INSERT INTO sessions ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", *vals
        )

    async def session(self, sid: int):
        return await self._one("SELECT * FROM sessions WHERE id = ?", sid)

    async def update_session(self, sid: int, **fields) -> None:
        sets = ", ".join(f"{k} = ?" for k in fields)
        await self._run(f"UPDATE sessions SET {sets} WHERE id = ?", *fields.values(), sid)

    async def due_picks(self):
        return await self._all("SELECT * FROM sessions WHERE mode = 'decide' AND status = 'open' AND pick_at <= ?", now().isoformat())

    async def due_reminders(self):
        soon = (now() + timedelta(hours=1)).isoformat()
        return await self._all(
            "SELECT * FROM sessions WHERE status = 'locked' AND reminded = 0 AND plan_at IS NOT NULL "
            "AND plan_at <= ? AND plan_at > ?",
            soon, now().isoformat(),
        )

    # ---- private answers

    async def save_answer(self, sid: int, user_id: int, data: dict) -> None:
        await self._run(
            "INSERT INTO answers (session_id, user_id, data_json, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(session_id, user_id) DO UPDATE SET data_json = excluded.data_json, updated_at = excluded.updated_at",
            sid, user_id, json.dumps(data), now().isoformat(),
        )

    async def answers(self, sid: int) -> dict[int, dict]:
        rows = await self._all("SELECT user_id, data_json FROM answers WHERE session_id = ?", sid)
        return {r["user_id"]: json.loads(r["data_json"]) for r in rows}

    async def purge_old_answers(self) -> int:
        """Delete private answers for plans that ended more than ANSWER_RETENTION_HOURS ago."""
        cutoff = (now() - timedelta(hours=config.ANSWER_RETENTION_HOURS)).isoformat()
        rows = await self._all(
            "SELECT id FROM sessions WHERE COALESCE(plan_at, created_at) < ? AND status != 'purged'", cutoff
        )
        for r in rows:
            await self._run("DELETE FROM answers WHERE session_id = ?", r["id"])
            await self._run("DELETE FROM votes WHERE session_id = ?", r["id"])
            await self._run("UPDATE sessions SET status = 'purged' WHERE id = ?", r["id"])
        return len(rows)

    # ---- votes

    async def vote(self, sid: int, user_id: int, choice: int) -> None:
        if choice >= 0:  # one option vote per person; switching replaces it
            await self._run("DELETE FROM votes WHERE session_id = ? AND user_id = ? AND choice >= 0", sid, user_id)
        await self._run("INSERT OR IGNORE INTO votes (session_id, user_id, choice) VALUES (?, ?, ?)", sid, user_id, choice)

    async def tally(self, sid: int) -> dict[int, int]:
        rows = await self._all("SELECT choice, COUNT(*) AS n FROM votes WHERE session_id = ? GROUP BY choice", sid)
        return {r["choice"]: r["n"] for r in rows}


def dumps(obj) -> str:
    return json.dumps(obj, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
