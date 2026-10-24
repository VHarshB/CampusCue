# GitHub Issues — copy/paste once repo is created

Create these five Issues under **Issues → New issue**. Assign actual GitHub usernames; use labels. **Every owner can begin immediately.** Mark acceptance criteria only after demonstrating real behavior.

## Issue 1 — `[LEAD] Public repo, integration, install & submission`
**Owner:** Repo/Team Lead  
**Labels:** `track-1`, `integration`, `submission`

**Tasks**
- [ ] Create public repo; push README, SKILL and docs; invite collaborators.
- [ ] Enable Issues; create and assign all five; set milestone / cutoff time from official site.
- [ ] Set rule: only PRs merge to main, reviewed by one teammate.
- [ ] Integrate B's verified events findings and A's Skill changes.
- [ ] Help C install and test Skill from pinned commit; record successful SHA.
- [ ] Submit one-liner, GitHub Skill link, team entry and optional video URL on official site.

**Done when:** Track 1 has a submitted, working Skill link and a demonstrated real test. No invented capability claims.

## Issue 2 — `[AGENT A] Skill workflow + schedule, mood, privacy`
**Owner:** Agent Builder A  
**Labels:** `track-1`, `skill`

**Tasks**
- [ ] Improve `SKILL.md` description + trigger examples (“what should I do right now”, “free between classes”).
- [ ] Define schedule checking with Google Calendar; fallback when unlinked.
- [ ] Accept user-shared current building; never assume calendar location is live GPS.
- [ ] Extract mood, social preference, price cap from user's message; minimize follow-up questions.
- [ ] Return one best activity + one backup, with source and reason; no event/no-info fallback.
- [ ] Consent rule for remembering preferences, RSVP, reminders or messages.
- [ ] Submit a PR with 3 example input/expected-output pairs (clearly marked examples).

**Done when:** Skill has clear triggers, a deterministic workflow, safe defaults, concise iMessage output and understandable fallback instructions.

## Issue 3 — `[AGENT B] ASU event discovery + feasibility checks`
**Owner:** Agent Builder B  
**Labels:** `track-1`, `events`, `research`

**Tasks**
- [ ] Try Cubbie's actual access to Sun Devil Central; record what is native, web-accessible, login-required, or blocked.
- [ ] Document fallback from official ASU Events pages where useful.
- [ ] Write and test recommendation constraints: actual date/time, venue, eligibility, registration, cost, feasibility before next class.
- [ ] Propose how to calculate usable time from free-time window and conservative transition buffer without inventing route duration.
- [ ] Supply 2–3 **real URLs** from current official sources that C can use to test (do not invent live events).
- [ ] Comment precise recommended changes to SKILL.md; open PR only for agreed section to avoid clashes with A.

**Done when:** There is a tested way to find real ASU options or an honest, verified fallback; Cubbie never fabricates availability or real-time proximity.

## Issue 4 — `[AGENT C] Install, QA matrix, video proof`
**Owner:** Agent Builder C  
**Labels:** `track-1`, `qa`

**Tasks**
- [ ] Keep [`TEST_PLAN.md`](TEST_PLAN.md) updated with prompts and pass/fail screenshots.
- [ ] Test public GitHub link installation on a real Cubbie account, including explicit yes/permissions.
- [ ] Test event-match, no-match, calendar unlinked, unknown location, budget, campus switch, no fake matchmaking, RSVP consent.
- [ ] For each failure, create Issue with input, response, expected behavior and screenshot (redact personal info).
- [ ] Share **real screen recording** for video lead once a normal prompt works.
- [ ] Approve final tested commit SHA / send team-lead release check.

**Done when:** Core happy path plus safety/fallback paths have documented evidence and the proposed demo is honest.

## Issue 5 — `[VIDEO] 58-second premium demo + vote launch`
**Owner:** Video Lead  
**Labels:** `track-1`, `video`, `marketing`

**Tasks**
- [ ] Read [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md), choose actor, campus filming spots and shot order.
- [ ] Start filming B-roll **before** software is done. Obtain consent from anyone identifiable.
- [ ] Create 9:16 1080x1920 draft with voiceover, natural ambience, subtitles, title slate.
- [ ] Leave editable placeholder for **QA's real** Cubbie output (do not fake results).
- [ ] Integrate verified screen recording and official source link when ready.
- [ ] Export sub-60s version and a silent-readable check; seek team sign-off.
- [ ] Prepare accurate caption + voting CTA, then post optional social link after launch rules confirmed.

**Done when:** Video tells a complete, authentic story in under 60 seconds and doesn't promise live GPS or stranger matching.

---

**Parallel rule:** A builds Skill; B validates event access; C preps QA; Video shoots B-roll; Lead sets repo. Everyone posts blockers in their Issue immediately. The signup form advertises at most four registered teammates; confirm role/headcount with the organizers if five people are involved.
