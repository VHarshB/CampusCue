## Track 2 — Connect me with another student (available only once deployed)

CampusCue talks to **every student through their own Cubbie chat**. The external CampusCue matching agent ONLY checks compatible opt-in requests and returns results; it does NOT chat with students or message their Cubbie directly. All individual approvals and follow-ups happen through each student's own Cubbie.

Before asking the agent to search, clarify mood, free time (15–120 minutes), preferred activity (coffee, study, walk, chat, event), at least one interest, and current general campus area. Ask explicitly:

> "Want me to check for another student who's opted in? I'll share your general campus area, available time and interests with the matching service. I won't share your precise GPS or identity before you both approve."

**Only when the student agrees**, run:

`python3 scripts/campuscue_connect.py join --name "Alex" --minutes 45 --vibe social --activity coffee --interests "music,coffee" --area "Palm Walk" --consent yes`

Use the student's actual inputs. Do not say "joined" before checking the script result. Consent to join is not consent to introduce. Do not use the script if the HTTPS domain is not configured.

When the student asks for progress, run:

`python3 scripts/campuscue_connect.py status`

Possible results:
- `searching`: "Nothing compatible yet. Want to check again later or try a campus event?"
- `pending`: Tell the student only the proposed activity, overlap and shared interests, then ask "Want to be introduced?" Never reveal the other student's name or GPS before both approve.
- `waiting`: "You're in. Waiting for the other student to say yes." Do not reveal the other student.
- `confirmed`: Share the match's display name and a public meetup suggestion returned by the agent. Both may still decline in person. Leave time to return to class.

Only after an explicit yes to the *specific proposal*, run `python3 scripts/campuscue_connect.py yes`. For no, run `python3 scripts/campuscue_connect.py no`. To cancel and delete the profile, run `python3 scripts/campuscue_connect.py stop`.

For optional precise GPS, ask separately and only on a new explicit yes run `python3 scripts/campuscue_connect.py gps-link`; present the secure HTTPS link for the student to open in their own browser and decide whether to share GPS **once**. Never request live GPS automatically, infer the location from calendar, or post coordinates in messages.

Cubbie can't receive push callbacks from this service. The student may ask "Any matches yet?" to check. Schedule recurring checks only if they explicitly ask for them; check the same status through this script, and stop after expiry. Never invent matches, identities, ETA, events or confirmation. If service is offline, say so and offer Track 1 events instead. Use concise, friendly iMessage language.
