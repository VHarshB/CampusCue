# Cubbie integration checklist

1. Deploy `track2/` to an HTTPS domain. Set `PUBLIC_BASE_URL` to the exact public URL.
2. Put `cubbie-addon/scripts/campuscue_connect.py` into your existing Skill's `scripts/` directory and update its `DEFAULT_BASE_URL`.
3. Copy `cubbie-addon/cubbie.yaml.example` to Skill root as `cubbie.yaml`, replacing the hostname placeholder. This declares access for Cubbie's code sandbox.
4. Append `cubbie-addon/SKILL-section.md` to the existing Skill. Do not replace the Track 1 instructions.
5. Install the branch-specific Skill into two distinct Cubbie users' chats. Get explicit opt-in separately, then demonstrate anonymous proposal, one yes (still private), second yes (introduction), and stop.
6. If status remains searching, check both opted into the **same campus area**, overlapping time, compatible mood/activity and at least one shared interest. Tokens must remain private.

No direct cross-Cubbie calls, unsolicited DMs, or automatic GPS. The backend is agent 2; Cubbie is each student's agent 1.
