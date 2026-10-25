## Share with friends (Rally)

Use this when the student wants to bring friends to a pick, e.g. "share with my friends", "send this to the group", or "see who's down".

1. If they haven't connected Rally yet, tell them in one short message: type `/rally link` in their Discord group chat and text you the code it shows. When they send `connect Rally <code>`, run:
   python3 scripts/share_to_rally.py connect --code <code>
2. To share, confirm first in one line ("Post Salsa Night, Fri 7 pm at the MU, to your group?") and wait for their yes. Then run:
   python3 scripts/share_to_rally.py share --title "<event name>" --url "<official event link>" --starts-at "<start, ISO 8601 with -07:00>" --location "<place>" --name "<their first name, if they've told you>"
3. If the script prints NOT_CONNECTED, explain step 1. If it prints FAILED, say Rally couldn't be reached and offer to try again later.
4. On success, reply in one line: "Posted to your group. Rally will run the poll and the meetup time."

Only share event details. Never send the student's mood, location, calendar or other private details to Rally.
