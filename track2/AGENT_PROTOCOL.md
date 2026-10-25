# Track 2 personal-agent protocol

**Trigger:** A student explicitly asks to meet somebody or explicitly opts in via the prototype. Mood alone is NOT permission to search.

## Agent A ↔ Agent B

1. **A's student opts in** and chooses time window, mood, desired activity, shared interests, general area, and optional alternative activities. Agent A stores these temporarily.
2. **B's student separately opts in** with their own settings. Agent B stores these temporarily.
3. Each agent evaluates the other independently and exchanges *only* the derived constraints it may reveal: mutually acceptable activity, shared public interests, overlapping minutes, and whether proximity is within the student's opted-in limit. No name, precise GPS, exact class schedule, contact info, or private mood is disclosed to the peer.
4. If the activities conflict, agents consider alternatives **only when each student explicitly allowed them**. Otherwise neither agent proposes an introduction.
5. Each student independently receives an anonymous request for a meetup. Either can say **No** without explanation.
6. Only after **A=yes AND B=yes**, reveal optional display names and a suggested public ASU meeting point. Never reveal exact GPS coordinates.
7. Stop or expiry clears the temporary location and profile. Cancel if either student retracts permission.

## Real-world cautions

- Browser geolocation is **one-shot** and asks the browser for explicit permission. It's not background tracking. The API checks straight-line distance—not actual walking distance or physical safety.
- The current demo uses one memory-only matching server, two separate `PersonalAgent` objects, and optional Discord DMs; it **does not** integrate with Cubbie's internal messaging tools.
- The prototype uses a predetermined, documented public ASU meetup point rather than pretending to compute the optimal walkable spot.
- The matching logic is deterministic; LLM integration is not required for the prototype and should never control consent decisions.
