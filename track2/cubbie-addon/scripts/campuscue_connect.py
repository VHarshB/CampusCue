#!/usr/bin/env python3
"""Cubbie Skill bridge: each student's own Cubbie calls this, not the other student.
Only standard Python 3.12 modules. Token stays in Cubbie's private persistent sandbox.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Set this to the HTTPS domain hosting your matching agent before publishing the Skill.
DEFAULT_BASE_URL = "https://REPLACE-WITH-YOUR-HTTPS-DOMAIN.example"
BASE = os.getenv("CAMPUSCUE_MATCH_URL", DEFAULT_BASE_URL).rstrip("/")
DATA_DIR = Path(os.getenv("SKILL_DATA_DIR") or (Path.home() / ".campuscue"))
STATE = DATA_DIR / "track2-session.json"


def state_load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def state_save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chmod(STATE, 0o600)


def state_clear():
    STATE.unlink(missing_ok=True)


def call(route, *, payload=None, token=None):
    if "REPLACE-WITH" in BASE:
        raise ValueError("Configure the deployed HTTPS matching-agent URL first.")
    if not (BASE.startswith("https://") or BASE.startswith("http://localhost:") or BASE.startswith("http://127.0.0.1:")):
        raise ValueError("The matching-agent URL must use HTTPS (except local tests).")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = Request(BASE + route, data=body, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urlopen(req, timeout=10) as response:
            return json.load(response)
    except HTTPError as e:
        try:
            message = json.load(e).get("error", "Request failed")
        except Exception:
            message = "Request failed"
        raise ValueError(message) from None
    except URLError:
        raise ValueError("The matching agent is offline. Try again later.") from None


def render(out):
    # Never print the private bearer token to Cubbie's reply or logs.
    out = dict(out)
    out.pop("token", None)
    print(json.dumps(out, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="CampusCue Connect bridge")
    sub = p.add_subparsers(dest="action", required=True)
    j = sub.add_parser("join")
    for arg in ("name", "vibe", "activity", "interests", "area"):
        j.add_argument("--" + arg, required=True)
    j.add_argument("--minutes", required=True, type=int)
    j.add_argument("--alternatives", default="")
    j.add_argument("--consent", choices=["yes"], required=True)
    for name in ("status", "yes", "no", "stop", "gps-link"):
        sub.add_parser(name)
    a = p.parse_args()
    try:
        session = state_load()
        if a.action == "join":
            if session.get("token"):
                raise ValueError("Matching is already active. Use status or stop first.")
            payload = dict(name=a.name, vibe=a.vibe, activity=a.activity, interests=a.interests,
                           area=a.area, minutes=a.minutes, alternatives=a.alternatives, consent=True)
            result = call("/api/join", payload=payload)
            token = result.pop("token")
            state_save({"token": token})
        else:
            token = session.get("token")
            if not token:
                raise ValueError("No active opt-in session. Ask the student before joining matchmaking.")
            if a.action == "status":
                result = call("/api/status", token=token)
            elif a.action in ("yes", "no"):
                result = call("/api/approve", token=token, payload={"approve": a.action == "yes"})
            elif a.action == "gps-link":
                result = call("/api/gps-link", token=token, payload={})
            else:
                result = call("/api/stop", token=token, payload={})
                state_clear()
        render(result)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
