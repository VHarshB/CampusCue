# CampusCue — Make Your Gap Count

**Cubbie Hackathon · Track 1: Cubbie Skills · Track 2: Agent-to-Agent Coordination**  
**Built around Arizona State University campus life**

> **The promise:** In the 45 minutes before class, find something meaningful to do—or, in our Track 2 vision, another consenting student to do it with.

CampusCue is a conversational Cubbie Skill that first understands the student's **mood, intention, free time, and voluntarily shared location**, then gives one actionable recommendation. It should feel like texting a campus friend, not searching an event directory.

## The problem
Students are surrounded by activities and other students, but a short break between classes can still feel boring or lonely. Event lists usually don't answer: **“What should *I* do, right here, before my next class?”** Nor do they create a safe introduction between two students who both want to connect.

## The idea: a choice that fits your vibe

1. Student: “Cubbie, I have 45 minutes before class.”
2. CampusCue: “What's your mood? What are you in the mood to do?”
3. Student: “A little lonely. I want to meet people.”
4. CampusCue: **“Would you rather join a quick campus event, or meet someone new?”**
5. The student chooses. CampusCue uses their available time, general location, preferences, and constraints.
6. **Quick event:** Get one feasible option from verified university sources. **Meet someone:** Use a mutual-consent agent matchmaking flow *only if the separate Track 2 system is actually available*.
7. Help the student return to their next class on time.

If the student already provides mood, activity, time, or location, **don't ask again**. At most two short questions in a message; be concise and warm.

## Tracks: one idea, two levels

| | **Track 1 — CampusCue Skill (working foundation)** | **Track 2 — CampusCue Connect (separate prototype)** |
|---|---|---|
| Student goal | Find a nearby event/activity fitting their mood and schedule | Connect with another compatible student who also opts in |
| Understand mood, time, interests | Cubbie conversation + connected calendar where permitted | Each student's own personal agent |
| Location | Student-shared campus/building | Shared **approximate area** only with time-limited consent; more precision only after separate approval |
| Discovery | Official campus event sources | Two agents exchanging minimal authorized preferences through an independently built channel |
| Result | One verified recommendation + optional backup | Compatibility check, two private approvals, then proposed **public** meeting place |
| Status | Implemented as a Skill workflow; must be validated on real Cubbie | **Not supplied by the Track 1 Skill alone. Build and demo separately.** |

### Track 1: what the Skill can actually do
- Ask about missing **mood, intended activity, free time, and location**.
- Offer social students **a quick event vs. meeting a person** as a meaningful choice.
- Use Cubbie's supported calendar, memory, web and browser capabilities with permission.
- Search [Sun Devil Central](https://sundevilcentral.eoss.asu.edu/), [ASU Events](https://events.asu.edu/) and [ASU Student Life](https://studentlife.asu.edu/whats-happening).
- Check event timing, campus/venue, registration, price, and practicality.
- Recommend one best activity, with its official source link; avoid invented data.
- Respond honestly when there are no options or no connected calendar.

**Current limitation:** A regular Cubbie Skill cannot discover other users, continuously read GPS, or have its scripts call Cubbie's internal tools. If Track 2 matching is not connected, it must **not pretend a student match happened**. It may suggest a real public social event instead.

### Track 2: the feature we want to build

**Two agents, two consenting students, one shared opportunity.**

```text
Student A                         Student B
    |                                 |
“I'd like to meet someone”     “Open to meeting people”
    |                                 |
A's agent: asks permission     B's agent: asks permission
    |                                 |
    +---- minimal opt-in preferences -+
                   |
       Compatible time + interests
          + approximate campus area
                   |
      A approves?     B approves?
                YES + YES
                   |
    Suggest public meeting point
         and confirm introduction
```

**Track 2 implementation requirements**
1. Two independently operated student agents, possibly in different supported messaging apps.
2. A working, consent-based agent-to-agent coordination channel; it may be hosted outside Cubbie as Track 2 permits.
3. Students choose whether to be discoverable, what to share, and for how long.
4. Compare **time overlap, approximate distance, compatible activity/mood, and user-stated preferences**; check both students' constraints.
5. Ask **both students independently** before revealing contact/meeting details or proposing an introduction.
6. Use public campus locations. Make requests expire and support decline, stop, block, and basic abuse safeguards.
7. Demonstrate what the agents share, how they resolve conflicts, and when they ask for human confirmation.

**Do not present Track 2 GPS sharing or matchmaking as a live Track 1 feature unless it really has been built and tested.** No automatic identification of nearby strangers.

### Track 3: later extension
CampusCue in an opt-in **group chat** could suggest one activity based on everyone's overlapping free time, budget, mood and approval. This is a separate Track 3 prototype, not part of the Track 1 Skill requirement.

## Example Cubbie conversation

**Student:** “I've got 45 minutes before my next class near Palm Walk.”  
**Cubbie:** “What's your mood—social, chill, or productive? Anything specific you feel like doing?”  
**Student:** “Feeling social. I want to meet people.”  
**Cubbie:** “Quick event or meet someone new?”  
**Student:** “Meet someone for coffee.”

**If a real Track 2 system is connected:**  
**Cubbie:** “Want me to look for another opt-in student? I'd only share your general campus area, interests, and available time.”  
Only after **both** independently approve may the agents arrange a public meetup.

**If it isn't connected:**  
**Cubbie:** “Direct student matching isn't live here yet, but I can find a nearby public social event where you can meet people. Want that?”

These conversations are intended behavior, **not claims of a verified match or event**.

## Repository files

```text
CampusCue/
├── README.md     # Project, scope, team plan, and release instructions
└── SKILL.md      # Instructions Cubbie installs and executes
```

A separate `cubbie.yaml` is needed **only** if the Skill invokes extra scripts that need declared packages, network hosts, secrets or login steps. Don't invent a `cubbie.yaml` for built-in Cubbie abilities.

## Install and test Track 1

1. Keep this repository **public** and place `SKILL.md` at the repository root.
2. Text Cubbie: **https://github.com/VHarshB/CampusCue**
3. Review Cubbie's summary and reply **yes** to install.
4. Test this message:

   > “I have 45 minutes free near Hayden Library. I'm feeling social. What should I do?”

5. Check that Cubbie asks **quick event or meeting someone**, if the intention isn't clear, and uses real event information if an event is chosen.
6. After modifying the file in GitHub, tell Cubbie **`update campuscue`**, approve the new version, and confirm which commit was installed.

An installed Skill is pinned to a GitHub commit; pushing a change alone does not update existing installations.

## Acceptance tests

| Test | Expected behavior |
|---|---|
| “I'm bored.” | Asks about mood and desired activity, rather than listing events |
| “I'm social and want to meet people.” | Offers **event or person** if not already specified |
| “I want a free campus event; 45 minutes, near Hayden.” | Searches real sources without repetitive questions |
| “Meet someone nearby.” | Asks for consent; **no fake match** if no Track 2 integration exists |
| Both agents opt in with overlapping windows | Only a *real Track 2 implementation* can propose a mutual match; both approve |
| One agent/student declines | No introduction and no disclosure of private details |
| Calendar isn't connected | Uses time stated by the student; never invents class time |
| No event available | Honest no-match response and realistic alternative |
| Location not shared | Asks for general building/campus, not continuous GPS |
| “I need to get to class soon.” | Leaves return buffer; no invented route times |

Record the **real Cubbie output** before calling a feature verified.

## Team responsibilities

| Workstream | Ownership / deliverable |
|---|---|
| **Integration & submission** | Repository, GitHub Issues/PRs, installed commit, organizer submission |
| **Track 1 Skill behavior** | Mood-first and event-or-person dialogue, short answers, boundaries |
| **Data & discovery** | Verify current ASU events, registration, distance/time feasibility |
| **Agent-to-agent prototype** | Independent student agents, opt-in protocol, compatibility and confirmation (Track 2) |
| **QA & video** | Actual Cubbie testing, real screen recording, film/edit; Track 2 visuals labeled accurately |

Some workstreams can be shared by one person. Follow the hackathon's stated **maximum of four registered team members**.

**Development flow:** Make GitHub Issues → claim owners → create branches → review PRs → test on a real Cubbie account → record commit and results → submit.

## Demo storytelling (under one minute)
A student sits alone on ASU's Palm Walk, with 45 minutes until class. He texts Cubbie. It asks about his mood, then offers **quick event or meet someone**. After learning his preference, CampusCue finds a realistic activity. He goes, meets people naturally, and arrives at class happier. Briefly reveal a **clearly labeled Track 2 concept**: two student agents coordinating an optional introduction after **two separate yeses**.

**Use authentic Cubbie results for Track 1. Label staged or future Track 2 screens as concept footage.**

## Before submitting
- [ ] The Skill installs from this public repository.
- [ ] Mood and **event-or-person** conversation works.
- [ ] One verified event recommendation or honest fallback works.
- [ ] Track 2 matching is demonstrated **only if actually built**, with mutual consent.
- [ ] Personal student information is removed from demo captures.
- [ ] The tested GitHub commit is recorded.
- [ ] Official form and cutoff requirements are confirmed.

**Hackathon:** https://hackathon.cubbie.ai/  
**Developer kit:** https://github.com/imaginix-inc/cubbie-hackathon-kit  
**Skill guide:** https://hackathon.cubbie.ai/skill.md

---

**One student's free time could be another student's free time too.**  
**CampusCue makes the connection meaningful—and consensual.**

**Make Your Gap Count.**
