#!/usr/bin/env python3
"""Share a CampusCue pick into the student's Rally group chat on Discord.

Standard library only, so cubbie.yaml needs no packages. Two commands:

  python3 scripts/share_to_rally.py connect --code K7Q2AB-MX9P41
  python3 scripts/share_to_rally.py share --title "Salsa Night" --url https://... \
      --starts-at 2026-10-30T19:00:00-07:00 --location "Memorial Union" --name Maya

The code is saved in the student's private Skill storage ($SKILL_DATA_DIR), so they connect once.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Replace with your deployed Rally address, and put the same host name in cubbie.yaml.
RALLY_URL = os.environ.get("RALLY_URL", "https://YOUR-RALLY-APP.up.railway.app")

STATE = Path(os.environ.get("SKILL_DATA_DIR", Path.home() / ".config" / "campuscue")) / "rally.json"


def load_code() -> str | None:
    try:
        return json.loads(STATE.read_text()).get("code")
    except (OSError, ValueError):
        return None


def connect(code: str) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"code": code.strip().upper()}))
    print("Connected to Rally. Say \"share with my friends\" after a pick to post it in your group chat.")


def share(args: argparse.Namespace) -> None:
    code = load_code()
    if not code:
        print("NOT_CONNECTED: ask the student to type /rally link in their Discord group and text you the code.")
        sys.exit(2)
    body = {k: v for k, v in {
        "code": code, "title": args.title, "url": args.url, "starts_at": args.starts_at,
        "location": args.location, "note": args.note, "shared_by": args.name,
    }.items() if v}
    req = urllib.request.Request(
        RALLY_URL.rstrip("/") + "/share",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(json.loads(r.read()).get("message", "Shared."))
    except urllib.error.HTTPError as e:
        detail = json.loads(e.read() or b"{}").get("detail", "")
        print(f"FAILED ({e.code}): {detail or 'Rally rejected the request.'}")
        sys.exit(1)
    except urllib.error.URLError:
        print("FAILED: couldn't reach Rally. It may be offline; try again in a minute.")
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("connect")
    c.add_argument("--code", required=True)
    s = sub.add_parser("share")
    s.add_argument("--title", required=True)
    s.add_argument("--url")
    s.add_argument("--starts-at", help="ISO 8601 with offset, e.g. 2026-10-30T19:00:00-07:00")
    s.add_argument("--location")
    s.add_argument("--note")
    s.add_argument("--name", help="The student's first name, shown in the group")
    args = ap.parse_args()
    connect(args.code) if args.cmd == "connect" else share(args)


if __name__ == "__main__":
    main()
