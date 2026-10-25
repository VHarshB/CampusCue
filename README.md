# Rally: turn "anyone down?" into a plan

**Cubbie Hackathon · Track 3: Group Chat Assistant · Arizona State University**

Rally is a Discord bot that joins your friend group's chat and gets plans out of the "maybe" stage. Find an event with CampusCue on Cubbie, share it to the group, and Rally runs the poll, works out a meetup time that suits the people who said yes, and locks it in with a reminder. When the group can't agree on something, like where to eat, Rally privately asks each person's limits and preferences and only puts options that work for everyone up for a vote.

> **CampusCue makes your gap count. Rally brings your friends.**

## Why students need it

Group plans die in the chat. Someone shares an event, three people say "maybe," and nobody goes. Someone asks "where do we eat?" and twenty minutes later nobody has decided, often because people don't want to say out loud "I can't afford that," "I'm under 21" or "I want a chill night." Rally asks privately and decides in public, so that friction disappears.

## What Rally does

### 1. Share from Cubbie
- Type `/rally link` in your group and text the code to Cubbie once.
- When CampusCue suggests an event, reply "share with my friends." It shows up in the group and starts Squad mode.
- Or just paste a Sun Devil Central link in the chat.

### 2. Squad mode: from "anyone down?" to a plan
1. Rally posts the event card with **I'm in / Maybe / Can't**.
2. In and Maybe open a private form: when you can get there, when you need to leave, and whether you need a ride or can drive.
3. Rally keeps a live suggestion on the card, like "Meet at the MU, 6:50 pm (3 of 4 can make it)."
4. The group taps **Lock it in**. Rally adds it to the server's Events and asks "still coming?" an hour before.

### 3. Decide mode: when the group can't choose
1. `/decide dinner tonight?`
2. Everyone taps **Share my preferences** and fills a private form:
   - **Limits** (must-haves): budget, diet, free time, under 21 or sober
   - **Preferences** (nice-to-haves): cravings, drinks or no drinks, and vibe from chill to party
   - One anonymous **veto**
3. Rally drops anything that breaks someone's limits, ranks the rest by everyone's preferences, and posts the top 3 for a vote.
4. When vibes clash, it favors middle-ground picks or suggests a two-part night: dinner together, then a party spot for whoever's still in.

## Privacy and consent

- Limits and preferences, including age and alcohol, are always private. Only Rally sees them.
- The group only sees counts ("4 of 5 can make it") and features of the options ("has vegetarian options"). A 21+ place dropped because someone is under 21 just disappears, and nobody is singled out.
- Private answers are deleted 24 hours after the plan.
- Nothing is committed until the group votes **Lock it in**, and `/rally pause` stops Rally in a channel.

## How it's built

| Piece | Tool |
| --- | --- |
| Bot | Python 3.12 + discord.py: slash commands, buttons, private forms, scheduled events |
| Reading casual answers | Claude API with structured outputs (keyword parser as a fallback) |
| Choosing the plan | Plain Python (`rally/rally/solver.py`), predictable and explainable |
| Cubbie connection | FastAPI web API (`POST /share`) plus a CampusCue script |
| Storage | SQLite |
| Hosting | Railway |

## Repository layout (this branch)

| Path | What's there |
| --- | --- |
| [`rally/`](rally/) | The Rally bot: code, data, tests, and the [full setup guide](rally/README.md) |
| [`campuscue-addon/`](campuscue-addon/) | Files to add to the CampusCue Skill so "share with my friends" posts to Rally |
| `SKILL.md`, `TEST_PLAN.md` | CampusCue, our Track 1 Cubbie Skill (its project page is the [README on `main`](https://github.com/VHarshB/CampusCue/blob/main/README.md)) |

## Quick start

```bash
cd rally
pip install -r requirements.txt
cp .env.example .env      # add your Discord bot token (and optionally a Claude API key)
python -m rally
```

Then try `/rally help`, `/decide dinner tonight?` or `/squad` in your server. Creating the Discord bot, deploying to Railway and connecting CampusCue are covered step by step in [rally/README.md](rally/README.md).
