# Upload Track 2 to matchmaking

Direct GitHub write access from ChatGPT returned 403, so this pack is ready for manual upload.

1. Go to https://github.com/VHarshB/CampusCue/tree/matchmaking/track2
2. Replace the old `track2` files with the files inside this ZIP's `track2/` directory. Remove old `src/discord.js` and the old dual-agent browser demo; they are not part of the new architecture.
3. Commit directly to the **matchmaking** branch (not main or rally-bot).
4. In `track2/`, run `npm test` and `npm start`.
5. Follow `track2/README.md` to deploy the HTTPS coordinator and add the Cubbie Skill bridge in a test branch. Never commit real tokens or private student location data.

**Architecture:** each student chats only with their own Cubbie; a single central matching service compares opted-in profiles and requires both approvals.
