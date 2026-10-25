# Track 2 handshake

**Roles:** Cubbie A, Cubbie B, etc. are the only student-facing agents. CampusCue Match is the central matching/coordinating agent. No student talks directly to it.

1. Each student tells their own Cubbie they want a meetup.
2. Cubbie privately asks about mood, preferred activity, interests, free time, general area, and explicit opt-in. No raw calendar or GPS is needed.
3. After opt-in, each Cubbie calls `POST /api/join` through its private Skill script. Its returned bearer session token is saved only in that Cubbie user's private sandbox.
4. Match agent compares sessions, including mood compatibility, shared interests, 15-minute overlapping availability and permitted proximity, then returns an anonymous proposal on `GET /api/status`.
5. Each Cubbie privately asks its own student if they agree to the **specific** introduction and calls `POST /api/approve`. Before both yeses: neither identity, contact data, GPS nor exact meetup is revealed.
6. After both yeses: each Cubbie can fetch the confirmed match and recommend a public meeting location. The students can still decline or cancel.
7. `POST /api/stop` deletes the student's temporary record. Automatic expiry removes stale sessions.

**GPS:** Optional secondary browser link. Cubbie may show it only with explicit consent. The server checks location privately; other students never get coordinates or live tracking. If no GPS, only identical voluntarily shared campus-area names are matched.

**Delivery limit:** Matching agent does not send messages into Cubbie or discover Cubbie accounts. Cubbie must run its own script to ask the server for status; it can schedule checks only with the student's permission. This keeps the demo real, not a fake cross-account Cubbie integration.
