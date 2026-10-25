# Connecting Track 1 CampusCue to Track 2 later

Track 1's Cubbie Skill can offer the choice: **"Quick event or meet someone?"**

If the student chooses **meet someone**, Cubbie must ask explicit permission to initiate matching and share *only* permitted fields. Then it can send them to the **separately deployed** Track 2 agent service through a declared HTTPS host and an authenticated, student-linked handoff.

**Not connected yet.** The existing Track 2 demo does **not** provide a secure Cubbie sign-in / identity handshake, and the browser server is localhost-only. Do not add a hardcoded URL or credentials to Track 1's SKILL.md. Do not tell students matching is live in Cubbie until authentication, access control and end-to-end tests exist.

For Track 2 judging, you can demo directly through the Discord DM adapter or the two-session web demo. The hackathon explicitly permits Track 2 to be built separately from Cubbie.
