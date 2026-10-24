# CampusCue — Make Your Gap Count

**Cubbie Hackathon · Track 1 · ASU**  
**One-liner:** CampusCue turns an awkward gap between classes into one nearby activity that fits your **free time, current location, mood, budget, and social energy**.

> **Team north star:** Not another list of campus events. One actionable, verified suggestion for *this student, right now*.
>
> **Current status:** Skill drafted, **not yet confirmed working on a real Cubbie account**. Do not present a mockup as a live result.

## 🔥 Everyone starts here — parallel ownership

**Create 5 GitHub Issues** using the exact titles below (issue instructions: [`docs/GITHUB_ISSUES.md`](docs/GITHUB_ISSUES.md)). Assign one owner to each, add a due time, and move them across **Todo → In progress → Review → Done**. Replace role placeholders with GitHub handles. These are *workstreams*, not a claim that five people are eligible to register; see team-size note below.

| Owner / issue | Starts immediately | Deliverable / definition of done |
|---|---|---|
| **You — #1 Repo & Integration** | Invite collaborators; enable Issues; create issue board; protect `main`; confirm hackathon cutoff | Installed real Skill, merged reviewed PRs, tested commit URL, final submission |
| **Agent Builder A — #2 Skill Behavior** | Own `SKILL.md` triggers, consent, calendar/mood logic | Natural text activates Skill; asks only for missing info; one pick + backup; safe fallback |
| **Agent Builder B — #3 ASU Events & Feasibility** | Verify Sun Devil Central retrieval; event filters; time/location constraints | Genuine source links; eligibility/time check; reliable no-match behavior; report access blockers |
| **Agent Builder C — #4 Test & Reliability** | Write/execute tests, test Cubbie install, document failures | Evidence for successful real-account run; no fake GPS or friend-matching; sanitized demo recording |
| **Video Lead — #5 Film & Social Launch** | Scout locations, film campus B-roll, plan edit/storyboard now | 55–60-second vertical cinematic video with **real** Cubbie output inserted after testing |

**Do not wait for each other:** A works on Skill wording, B investigates event access, C prepares tests, Video Lead shoots B-roll, and you set up the repo/issues **in parallel**. Video Lead gets the real-screen recording from C after first verified pass.

**Registration caution:** The hackathon form currently specifies **up to 4 team members**. If all five workstreams belong to five different people, confirm with organizers whether a separate video collaborator is allowed/how to credit them. Consolidate roles if only four people are registered.

## 🎯 The exact problem and MVP

> “I have 45 minutes before my next class. I'm near Hayden Library and want to be social, but don't want to spend money. What's one thing I can do?”

CampusCue should:

1. **Free time:** Read a connected Google Calendar with user permission, or use the student's stated time. Do not assume Canvas deadlines imply physical class times.
2. **Current location:** Use a building / area shared **on demand**. A calendar location is *not* the student's live GPS. Native continuous GPS is not a documented Skill ability.
3. **Mood + social intent:** Understand what the student said (social, tired, focused, bored, wants company, wants solitude), and use optional budget/preferences.
4. **Real campus discovery:** Prefer ASU **Sun Devil Central**; check the official event/venue page, with ASU Events as a fallback. The team must **verify** that Cubbie can retrieve specific listings. Do **not** assume a native Sun Devil Central integration exists merely because a website is available.
5. **Make it feasible:** Verify timing, venue, drop-in eligibility, cost (if published), and travel/transition buffer before the next commitment. Do not manufacture walking ETAs.
6. **One pick + one backup:** Explain *why* it fits, link the source, and offer directions / reminder / social icebreaker if appropriate. Ask before taking external action.

**Hard scope boundary for Track 1:** NO always-on GPS, NO cross-user matching, NO unsolicited location tracking, NO fake “students nearby,” NO backend or new app. Student-to-student introductions with consent and shared coordination belong to Track 2.

### Success = this specific behavior

- A student texts Cubbie naturally; the Skill activates.
- Student's time, volunteered location, and mood actually affect the recommendation.
- Result cites a **real, current source** with a joinable option **or honestly says no verified event fits**.
- The response is short enough for iMessage, never claims secret access to calendars, location or other students.
- Tested from a public GitHub commit on a **real** Cubbie account.

## 🎥 58-second video — script and shot plan

Full camera/edit instructions: [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md). **Shoot narrative B-roll now; insert authentic app footage later.**

| Time | Visual (9:16 vertical) | Narration / sound |
|---|---|---|
| **0–7 s** | Class ends. Student looks at phone: **45 MIN FREE**. Crowded ASU campus, yet they sit alone. | “Ever have 45 minutes between classes… and somehow nothing to do?” |
| **7–14 s** | Frustrated scrolling: crowded event lists, confusing options. Rack focus to students laughing in distance. | “Campus is full of people and events. But what’s actually for you, right now?” |
| **14–22 s** | Close-up: **real iMessage** to Cubbie: “45 min free. Near Hayden. Feeling social. Anything free?” | “So instead of opening five apps, I text Cubbie.” |
| **22–32 s** | Clean typography overlays: **TIME / LOCATION / MOOD**; then actual tested Cubbie response. | “CampusCue considers my free time, where I am, and how I’m feeling.” |
| **32–43 s** | Official ASU event page on phone; real best pick with source link; walking toward venue. | “It finds actual campus activities and recommends one that fits before my next class.” |
| **43–52 s** | Student hesitates at door, glances at Cubbie’s simple icebreaker, goes in and says hello. | “Even if showing up alone feels awkward, it helps with the first hello.” |
| **52–58 s** | Warm, candid moment with new acquaintances. End card: **CAMPUSCUE — MAKE YOUR GAP COUNT.** | “Less scrolling. More living. CampusCue. Built for Cubbie.” |

**Must stay honest:** If no real event qualifies when filming, show an actual no-event fallback with a verified campus activity instead. Do not stage the tool's answer as if the recommendation happened. Staged human interactions are fine as **illustrative lifestyle scenes**.

## 📂 Repository map

```
CampusCue/
├── README.md                  # Single source of truth: owners, scope, script, status
├── SKILL.md                   # Actual Cubbie Skill (install this)
├── docs/
│   ├── GITHUB_ISSUES.md       # Paste-ready Issues / acceptance criteria
│   ├── TEST_PLAN.md           # Real account test matrix and evidence table
│   └── VIDEO_SCRIPT.md       # Director-ready storyboard, VO, shot list, edit notes
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

## 🛠 Team GitHub rules

1. **Issues first.** Create the 5 issues from [`docs/GITHUB_ISSUES.md`](docs/GITHUB_ISSUES.md), assign owners and labels: `track-1`, `skill`, `events`, `qa`, `video`, `blocked`.
2. **One branch per issue:** e.g. `feature/skill-flow`, `research/event-source`, `test/cubbie-validation`, `docs/video`, `release/track1`.
3. **PR to `main`**, refer to its issue (`Closes #...`), and have at least one teammate review. **Do not all edit the same file at once.**
4. **Every bug gets an Issue** with test message, actual reply, expected reply, and sanitized evidence. Never commit calendar, names, private locations, passwords, or account tokens.
5. **Only one person merges/release-tags:** Repo & Integration lead. Agent Builder C gives QA approval; Video Lead uses only approved recordings.
6. **Push frequently**, and record decisions/blockers in the matching Issue. If blocked >20 minutes, post what failed and switch to independent work.

## ⏱ Build order (relative to kickoff)

- **Before / at start:** Repo, Issues, confirmed cutoff, event source reconnaissance, location scouting, shot list.
- **First work block:** A refines instructions, B tests real events, C writes scenarios, video shoots narrative scenes, you invite + coordinate.
- **Integration block:** Merge changes → text GitHub link to Cubbie → approve install → run actual scenarios → patch failures.
- **Freeze before cutoff:** Stop new features; get one clean end-to-end run, save tested commit, publish entry, capture real screenshots, final video.

Official site currently says Track 1 finishes within the **first 10 hours**, with exact cutoff to be confirmed. Check the live rules before relying on this timing: https://hackathon.cubbie.ai/

## 📲 Install, demo and submit

1. Make the GitHub repo **public**. Push `SKILL.md` at the repo root.
2. In your Cubbie iMessage chat, text the **actual repo URL** and say yes after reviewing the installation summary.
3. Run the test prompts in [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md). If Cubbie cannot access a source, record that and fix the flow; don't fabricate a result.
4. If you update the Skill, text Cubbie `update campuscue` and approve the new install (installed versions are pinned to a commit).
5. Record the **tested commit SHA/URL**, Skill link, one-line student use case, and approved optional public video URL.
6. Submit **Track 1** on https://hackathon.cubbie.ai/ before the cutoff. Track 1 is mandatory to unlock Track 2 and 3.

**Submission one-liner:** “CampusCue turns free time between classes into a real nearby activity tailored to your schedule, location, mood and social vibe.”

## 📌 Live launch tracker (update in every standup)

| Item | Status | Owner | Evidence / link |
|---|---|---|---|
| Repo public + collaborators invited | ⬜ | Repo lead | |
| GitHub issues assigned | ⬜ | Repo lead | |
| Skill logic / consent complete | ⬜ | Builder A | |
| Event source checked | ⬜ | Builder B | |
| Cubbie installs Skill successfully | ⬜ | Builder C + repo lead | |
| End-to-end recommended activity verified | ⬜ | Builder C | |
| 58-second demo with real result | ⬜ | Video Lead | |
| Track 1 submitted + commit recorded | ⬜ | Repo lead | |

## 🔗 Ground-truth references

- Hackathon rules: https://hackathon.cubbie.ai/
- Official Cubbie kit: https://github.com/imaginix-inc/cubbie-hackathon-kit
- Cubbie Skill guide: https://hackathon.cubbie.ai/skill.md
- ASU Sun Devil Central: https://sundevilcentral.eoss.asu.edu/
- ASU official events platform: https://events.asu.edu/
- ASU explanation of Sun Devil Central events: https://eoss.asu.edu/clubs/manage-your-student-organization

**Rule:** Cubbie’s access to Google Calendar depends on a student linking their account. Live native GPS / native Sun Devil Central integration have **not** been independently verified; test before claiming them in the video.
