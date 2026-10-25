# CampusCue Connect — Track 2

**Cubbie speaks to students. Our agent only matches them.**

```
Student A ↔ Cubbie A ──┐
                      ├── HTTPS ── CampusCue Matching Agent
Student B ↔ Cubbie B ──┘           (mood + time + interests + location + 2 approvals)
Student C ↔ Cubbie C ──┘
```

Every student keeps chatting with **their own Cubbie**, not our bot. A matching request contains only volunteered information. Our coordinator finds compatible opt-in students, checks schedules and general proximity, asks each student's Cubbie to collect approval, and returns a public meetup only after **both independently say yes**. No automatic GPS tracking.

## What works
- Real HTTP API for many Cubbie clients: join, status, approve, decline, stop.
- Matching based on shared interests, compatible activity/mood, overlapping time (15+ min), same general campus area **or separately authorized one-time GPS within 1.2 km**.
- Temporary private sessions (15–120 min) and 10-min proposals; declining blocks that pair for the session.
- No match identity or meeting location before both approvals. No raw GPS returned to another student.
- Optional one-time secure-browser GPS link; user must explicitly allow the phone's browser permission.
- Python bridge for Cubbie's Skill sandbox; session token saved privately per student.
- Automated API, consent and privacy tests.

**Status:** Prototype. Not deployed or tested in Cubbie yet. The existing `main` Track 1 Skill stays unchanged until integration is tested; `rally-bot` is the separate Track 3 project.

## Quick test locally

Requires Node.js 22+, Python 3.12+.

```bash
cd track2
npm test
npm start
```

In two **separate private HOME directories** (simulate two independent Cubbie student sandboxes):

```bash
export CAMPUSCUE_MATCH_URL=http://localhost:3000
export SKILL_DATA_DIR=/tmp/cue-student-a
python3 cubbie-addon/scripts/campuscue_connect.py join --name Alex --minutes 45 --vibe social --activity coffee --interests music,books --area 'Palm Walk' --consent yes

# Second terminal, independent session:
export CAMPUSCUE_MATCH_URL=http://localhost:3000
export SKILL_DATA_DIR=/tmp/cue-student-b
python3 cubbie-addon/scripts/campuscue_connect.py join --name Blair --minutes 35 --vibe chill --activity coffee --interests music,art --area 'Palm Walk' --consent yes
```

Then in each terminal run `... campuscue_connect.py status`, and when asked, `... yes`. Only after *both* yeses will a name and public meetup suggestion appear. Use `... stop` to delete a session.

## Deploy and connect to Cubbie

1. Deploy the **`track2/` folder** as a Node.js 22 web service on Railway/Render or your own HTTPS host. Start command: `npm start`. Root directory: `track2`. Set `PUBLIC_BASE_URL=https://YOUR-SERVICE-DOMAIN` and let the host supply `PORT`. Use an always-on instance for the live demo; server memory is not shared between replicas.
2. Verify `https://YOUR-SERVICE-DOMAIN/health` returns `ok:true`.
3. Copy `cubbie-addon/scripts/campuscue_connect.py` to the root Skill's `scripts/` folder; replace `DEFAULT_BASE_URL` with your deployed HTTPS URL.
4. Copy `cubbie-addon/cubbie.yaml.example` to the root Skill as `cubbie.yaml`; replace the placeholder with **hostname only**, no protocol/path.
5. Append `cubbie-addon/SKILL-section.md` to root `SKILL.md` and push to a test branch. Send that branch's Skill link to Cubbie; approve the update and test with **two different Cubbie accounts**.
6. Student A opts in through Cubbie; Student B opts in through their own Cubbie. Both ask "Any matches?" and approve independently. Record actual messages for the Track 2 demo. If either declines, no introduction.

Cubbie scripts call external HTTPS endpoints declared in `cubbie.yaml`; scripts **cannot** call Cubbie's internal messaging/calendar tools. Cubbie handles any calendar lookup and passes only the student's chosen free-time window to the script.

## API contract

Each student's Cubbie sandbox retains its own bearer token. Do not paste tokens into chat, logs or GitHub.

| Method | Endpoint | Cubbie does |
|---|---|---|
| POST | `/api/join` | Explicit opt-in and minimum profile; returns private token |
| GET | `/api/status` | Checks match and consent state; bearer token required |
| POST | `/api/approve` | `{ "approve": true/false }` on current proposal |
| POST | `/api/stop` | Deletes profile and pending request |
| POST | `/api/gps-link` | Requests 5-minute one-time optional GPS URL |
| POST | `/api/gps-once` | Secure browser submits location once after permission |

## Team tasks

- **Cubbie integration:** Set server hostname, Skill section and manifest; test on two real Cubbie chats.
- **Matching agent:** Improve ranking, safety checks, expiring proposals and logging; never bypass consent.
- **Deployment/QA:** Host HTTPS API, run tests with two real students, prove decline and disconnect.
- **Demo:** Show two Cubbies asking permission → shared-interest match → both yes → public meeting suggestion.

## Prototype limits

This is not suitable for public launch. No account verification, durable storage, sophisticated anti-abuse, moderation, live GPS, real-time push notifications or production rate limiting. In-memory state disappears on service restart. Do not recruit strangers or publish the service without safety hardening and a privacy review. Use test volunteers and public venues for the hackathon.
