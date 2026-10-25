# Rally: the group chat bot that turns "anyone down?" into a plan

**Cubbie Hackathon · Track 3 (Group Chat Assistant) · ASU**

Find an event with CampusCue on Cubbie, share it to your group chat, and Rally runs the poll, works out a meetup time that suits the people who said yes, and locks it in with a reminder. When the group can't agree on something, like where to eat, Rally privately asks each person's limits and preferences and only puts options that work for everyone up for a vote.

> CampusCue makes your gap count. Rally brings your friends.

## Features

| Feature | How it works |
| --- | --- |
| **Share from Cubbie** | `/rally link` gives the channel a code. Text it to Cubbie once (`connect Rally <code>`). After a CampusCue pick, "share with my friends" posts the event in the group. Pasting a Sun Devil Central link works too. |
| **Squad mode** | Event card with **I'm in / Maybe / Can't**. In and Maybe open a private form for arrival time, leave time and rides. Rally keeps a live suggested meetup time ("6:50 pm at the MU, 3 of 4 can make it"). **Lock it in** needs half of the people who are in. Rally then adds a Discord event and asks "still coming?" an hour before. |
| **Decide mode** | `/decide dinner tonight?` Everyone taps **Share my preferences** and fills a private form: budget, diet, free time, drinks and vibe, cravings and one anonymous veto. Rally reads it back to them privately, removes any option that breaks someone's limits, ranks the rest by everyone's preferences and posts the top 3 for a vote. |
| **Chill vs party** | When vibes clash, middle-ground options rank higher, and Rally suggests a two-part night (dinner together, then a party spot for whoever's still in). |
| **Privacy** | Limits and preferences, including age and alcohol, are always private. The group only sees counts ("4 of 5 can make it") and option features ("has vegetarian options"). Under-21 and sober answers quietly remove places and are never mentioned. Private answers are deleted 24 hours after the plan. |
| **Consent** | Nothing is committed until the group votes **Lock it in**. `/rally pause` stops Rally in a channel. |

## How it's built

One Python app runs the Discord bot and a small web API together.

| Piece | Tool |
| --- | --- |
| Bot | Python 3.12, [discord.py](https://discordpy.readthedocs.io/) 2.7: slash commands, buttons, private forms (modals), scheduled events |
| Reading casual answers | Claude API (`anthropic` SDK, structured outputs). Without a key, a keyword parser takes over |
| Choosing | Plain Python in `rally/solver.py`, no AI, so results are predictable and explainable |
| Web API for Cubbie | FastAPI + uvicorn: `POST /share`, `GET /health` |
| Storage | SQLite (`aiosqlite`) |
| Data | `data/places.json` (Tempe spots with price, diet, 21+, alcohol and vibe tags) and `data/events.json` (backup events) |
| Hosting | Railway with a volume (or a laptop + Cloudflare Tunnel) |

```
rally/
  rally/__main__.py   starts the bot and the web API
  rally/bot.py        commands, cards, buttons, private forms, reminders
  rally/solver.py     meetup time, limit filtering, preference scoring, chill-vs-party compromise
  rally/parse.py      Claude parsing of private answers, plus the keyword fallback
  rally/events.py     reads Sun Devil Central links (falls back to events.json)
  rally/api.py        POST /share for CampusCue
  rally/db.py         SQLite tables and the 24-hour cleanup
  data/               places.json, events.json
  tests/              pytest tests (no Discord or API key needed)
../campuscue-addon/   the files to add to the CampusCue Skill for "share with my friends"
```

## Set it up, step by step

### 1. Create the Discord bot (about 10 minutes)

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications), click **New Application**, and name it **Rally**.
2. Open **Bot**. Click **Reset Token** and copy the token. Keep it secret.
3. On the same page, turn on **Message Content Intent** (Rally uses it to notice pasted event links).
4. Open **OAuth2 → URL Generator**. Tick the scopes `bot` and `applications.commands`. Under bot permissions, tick **View Channels, Send Messages, Embed Links, Read Message History, Use Slash Commands, Create Events** and **Manage Events**.
5. Open the generated URL and add Rally to your test server.
6. In Discord, turn on **Settings → Advanced → Developer Mode**, then right-click your server and choose **Copy Server ID**. Commands show up instantly in that server.

### 2. Get a Claude API key (optional but recommended)

Create a key at [console.anthropic.com](https://console.anthropic.com/) under **API Keys**. Without it, Rally still works, using a simpler keyword parser for preferences.

Rally uses `claude-opus-5-5` by default, with low effort and server-side fallbacks turned on so a declined request is retried on another model. Set `RALLY_MODEL` to change it, for example `claude-haiku-5-5` for a cheaper option.

### 3. Run it on your laptop

```bash
cd rally
python3.12 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in DISCORD_TOKEN, DISCORD_GUILD_ID and ANTHROPIC_API_KEY
python -m rally
```

You should see `Rally is online as Rally#1234`.

### 4. Try it in Discord

- `/rally help`
- `/decide question: dinner tonight?`, then have 2 or 3 people tap **Share my preferences** with different budgets and vibes, then **Pick now**, vote and **Lock it in**.
- `/squad event: Salsa Night when: fri 7pm where: Memorial Union`, or paste a Sun Devil Central link. Tap **I'm in**, add an arrival time, then **Lock it in**.

### 5. Put it online with Railway

1. Go to [railway.app](https://railway.app/), choose **New Project → Deploy from GitHub repo**, and pick `VHarshB/CampusCue`.
2. In the service's **Settings**, set **Branch** to `rally-bot` (or `main` once merged) and **Root Directory** to `rally`.
3. In **Variables**, add `DISCORD_TOKEN`, `DISCORD_GUILD_ID`, `ANTHROPIC_API_KEY` and `RALLY_DB_PATH=/data/rally.db`.
4. Add a **Volume** mounted at `/data`, so the database survives restarts.
5. In **Settings → Networking**, click **Generate Domain**. Open `https://<your-domain>/health` and check it shows `{"ok":true}`.

Avoid Render's free tier: it puts apps to sleep, which disconnects the bot, and it wipes local files.

### 6. Connect CampusCue on Cubbie

1. Copy `campuscue-addon/scripts/share_to_rally.py` into a `scripts/` folder at the root of the CampusCue repo.
2. In that script, replace `YOUR-RALLY-APP.up.railway.app` with your Railway domain.
3. Copy `campuscue-addon/cubbie.yaml` to the repo root and put the same domain in it.
4. Paste `campuscue-addon/SKILL-share-section.md` into `SKILL.md` as a new section.
5. Push, then text Cubbie `update campuscue` and reply yes.
6. In Discord, type `/rally link`. Text Cubbie `connect Rally <code>`.
7. Ask CampusCue for something to do, then say "share with my friends". The event appears in Discord.

These files change the Track 1 Skill, so test them on a branch link first (text Cubbie the branch's folder link) before merging into `main`.

### 7. Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Before the demo

- Replace the sample events in `data/events.json` with real upcoming events, and never present a sample as real.
- Check every entry in `data/places.json`: prices, hours, age rules and menus change.
- Sun Devil Central may need an ASU login to read event pages. When Rally can't read one, anyone can tap **Edit details** to add the time and place.

## Demo script (about 2 minutes)

1. Text Cubbie: "45 min free near Hayden, feel social." CampusCue suggests an event. Reply "share with my friends."
2. The event appears in Discord. Three friends tap **I'm in**; show one private arrival form.
3. Rally suggests "Meet at the MU, 6:50 pm (3 of 4 can make it)." Tap **Lock it in**; the Discord event appears.
4. `/decide dinner after?` One person privately says "$10 max, vegetarian, under 21, chill"; another says "down to party, drinks". The vote shows only options that fit everyone, plus the two-part night idea, and nobody's details appear.
5. Close: "CampusCue makes your gap count. Rally brings your friends."
