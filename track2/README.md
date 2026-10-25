# CampusCue Connect — Track 2

**Two personal student agents. One compatible campus meetup. Two independent yeses.**

Track 1 (`main` branch) already handles mood-based events via Cubbie. This is a **separate Track 2 prototype**. Track 3's `rally-bot` branch is untouched.

## What is implemented

- Each student **explicitly opts in** for 15–120 minutes and gives a general campus area, free time, mood, activity and interests.
- Two **independent personal-agent instances** assess each other's constraints and negotiate a mutually acceptable activity (including explicitly allowed alternatives).
- Match only when there is a **15+ minute overlap**, shared interest, compatible mood, and compatible area or one-time GPS proximity (straight-line radius <= 1.2 km).
- The agents exchange **minimum information** (compatible activity, overlapping time, shared interests, pass/fail proximity), **never raw GPS**.
- Both students privately approve. **No identity or public meeting place is revealed until both say yes.**
- When accepted, show an ASU public landmark: **Memorial Union main entrance**, 301 E Orange St ([official ASU map](https://www.asu.edu/map/interactive/?psCode=MU)). Verify your route; this is an agreed suggestion, **not** proof the space is open.
- Decline, stop, 10-minute proposal expiry, and short-lived student sessions; profile/GPS deleted from server memory on stop or expiry.
- **Local browser demo** (two separate student sessions) and **optional Discord DM messaging** using one bot handling two separate personal agents.

> **Status:** The local Node.js prototype and automated tests work. Discord is an adapter, and must still be configured and tested with real Discord accounts. There is **no live Cubbie-to-Cubbie messaging**, persistent database, student ID verification, background GPS tracking, or production security. Do not advertise these features as live.

## Run the local demo — no API key, no installation packages

Requirements: Node.js 22 or newer.

```bash
cd track2
npm test
npm start
```

Open **http://127.0.0.1:3000** in Chrome and a **separate private/incognito window** (or two distinct browsers). Test both as independent students:

| Student A | Student B |
|---|---|
| Alex, 45 min, social, coffee, `music, coffee`, Palm Walk | Blair, 35 min, chill, coffee, `music, art`, Palm Walk |
| Click **opt in** | Click **opt in** |
| See anonymous proposal | See anonymous proposal |
| Click **Yes** | Click **Yes** |
| See the other name and public meetup | See the other name and public meetup |

Optional: each student can independently press **Share GPS once** (browser permission). Browser geolocation works only in secure contexts such as **localhost** or HTTPS. Raw coordinates are kept only in ephemeral server memory; they're never sent to the other student. Proximity is straight-line, **not a walking-time estimate**.

To show conflicting constraints, try `coffee` versus `walk` with no alternatives: no match. Then both can explicitly allow `walk` as an alternative and align their vibes: the agents negotiate a compromise without exposing private details.

## Discord DM demo (two actual messaging accounts)

This adapter allows each student to talk privately to the bot via Discord; a separate `PersonalAgent` acts on their behalf. It does **not** require Cubbie to message other students.

1. Create a Discord Application and Bot in the [Discord Developer Portal](https://discord.com/developers/applications), invite it to a small test server, enable **Message Content Intent**, and allow it to receive/send direct messages.
2. In `track2/` run `npm install`, then copy `.env.example` to `.env` and put your bot token in `DISCORD_BOT_TOKEN`. **Never commit `.env`.**
3. Start `npm run discord`.
4. Two Discord users separately DM the bot:

```text
!cue join 45 | social | coffee | music, books | Palm Walk | walk
!cue join 35 | chill | coffee | music, art | Palm Walk
```

Each receives its *own* private matching request. Each replies `!cue yes` or `!cue no`.

Other messages: `!cue help`, `!cue status`, `!cue stop`, `!cue gps`.

**Discord + GPS:** `!cue gps` works only when you set `PUBLIC_BASE_URL` to an HTTPS tunnel pointing to the local demo server. It sends a short-lived, single-use consent link. Users explicitly choose browser GPS access there; locations are never posted to Discord. Do **not** expose this demo service to untrusted users—it lacks production authentication and abuse controls.

## Architecture

```text
Student A → Discord DM / browser → Agent A ──┐
                                             ├→ Coordinator: availability + interests + proximity
Student B → Discord DM / browser → Agent B ──┘
                        |                       |
                    Ask A privately         Ask B privately
                        └──── YES + YES ────────┘
                               ↓
                     Public meetup suggestion
```

The engine is deterministic and explainable; it does **not** call an LLM. It is an *agent-to-agent prototype*, not a trained AI model. If judges require LLM reasoning, add it as an enhancement after this working consent foundation is stable. Never let an LLM override the approval rules.

## What team members can own

| Agent owner | Work |
|---|---|
| Member 1 | `src/engine.js`: scoring, schedule overlap, negotiation and privacy tests |
| Member 2 | `src/server.js`, `public/`: geolocation consent and browser experience |
| Member 3 | `src/discord.js`: Discord bot credentials, real two-account demos and failure handling |
| Lead | Integration, security review, demo recording, organizer requirements |

## Submission/demo checklist

- [ ] `npm test` passes.
- [ ] Two real student accounts or isolated browser sessions explicitly opt in.
- [ ] Both agents independently assess compatibility, including conflicting activities/vibes.
- [ ] One student approving never exposes the other's identity.
- [ ] A decline prevents introduction; stop/expiry erases location data.
- [ ] GPS request is *one time only*, separately consented, and never shown to the other user.
- [ ] Both approving reveals only the optional display name and a **public** meetup suggestion.
- [ ] If using Discord, verify working DMs end-to-end; screenshot consent and agent negotiation states.
- [ ] Show in demo when each agent asks its student to confirm, and what was shared between agents.
- [ ] Keep all changes on a separate Track 2 branch until reviewed; don't merge over Track 1 or `rally-bot`.

## Safety and scope

This is a **short hackathon demo**, not a publicly safe matchmaking system. Before launching to real students, add university account verification, moderation/reporting/blocking, rate limiting, TLS, durable encrypted short-lived storage, robust time-zone and route calculations, safety guardrails for abuse, and privacy/legal review. Users should only meet in visible public spaces and can change their minds at any time. Never silently track GPS or infer sensitive personal traits.
