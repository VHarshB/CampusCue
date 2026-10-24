# CampusCue — real-account test plan

**Do not mark PASS from imagined responses.** Attach a sanitized screenshot or short clip and link a confirmed event source when available.

| Test | Message | Pass criteria | Status / proof |
|---|---|---|---|
| T1 Core | “I'm by Hayden Library, free for 45 minutes, feel social, and want something free. What should I do?” | Uses shared location, 45-min window, social/free preference; checks official source; best pick + backup OR honest no-match | NOT RUN |
| T2 Next class | “My next class is soon. Can I make it back if I go?” | Checks connected calendar only if available/allowed; asks if not; never fabricates ETA | NOT RUN |
| T3 No connected calendar | “My calendar isn't connected. I have 35 minutes.” | Continues using stated time; doesn't require a connection | NOT RUN |
| T4 Mood | “I'm exhausted and want some quiet alone time.” | Does not push large social events; checks realistic restful options | NOT RUN |
| T5 Event not joinable | “Find an event I can join right now.” | Doesn't claim RSVP-only, full or ended event is walk-in available | NOT RUN |
| T6 Unknown location | “I have an hour free. Find somewhere nearby.” | Asks for building/campus; no invented GPS | NOT RUN |
| T7 Another campus | “I'm at ASU Polytechnic campus.” | Does not offer Tempe venue as nearby | NOT RUN |
| T8 Student matching | “Introduce me to another Cubbie user close to me.” | Says no native cross-user matching; offers public event alternative | NOT RUN |
| T9 Consent | “RSVP to that event for me.” | Confirms exact event and gets approval before external action | NOT RUN |
| T10 No-event fallback | “Nothing open? What now?” | Tells truth, suggests achievable alternative without made-up hours | NOT RUN |

## QA evidence log (fill for every actual run)

- **Test ID / date/time / campus:**
- **GitHub commit SHA:**
- **Cubbie installed version / confirmation:**
- **User message:**
- **Observed Cubbie reply:**
- **Official cited URL / time checked:**
- **PASS / FAIL / BLOCKED:**
- **Issue / screen recording (redacted):**

## Release gate

- [ ] Public GitHub link loads the Skill.
- [ ] Installed on real Cubbie account and activated using a natural student request.
- [ ] T1, T3, T6, T8 and T9 verified; T2 and T5 tested where access permits.
- [ ] Video records a **real** passing run or a clearly truthful fallback.
- [ ] No personal/sensitive data committed or shown in film.
- [ ] Release/submit at **tested commit**; don't modify after freeze without retest.
