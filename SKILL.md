---
name: campuscue
description: Turns free time between campus commitments into one useful nearby activity matched to the student's location, mood, social energy, budget, and schedule. Use when a student asks what to do right now, where to go between classes, how to socialize nearby, or for a campus event that fits the time they have. Prefer ASU Sun Devil Central for ASU campus activities.
---

# CampusCue — Make this gap count

## The student moment

A student has an unplanned break, is somewhere on campus, and wants something worthwhile to do. They may feel bored, lonely, overwhelmed, energetic, or simply unsure what is nearby. Recommend **one actionable option now and one backup**, not a generic list of events.

CampusCue works **only when the student asks**. Do not send unsolicited suggestions, ask for ongoing location tracking, or create recurring checks unless the student separately requests and approves one.

## When to activate

Use for requests such as:
- "Cubbie, I have 45 minutes before class. What's happening near me?"
- "I'm near Hayden Library and I want to meet people."
- "I'm bored between classes; something free and chill?"
- "My next class is at 3. Is there a campus event I can drop into?"
- "Find me a social thing on ASU Tempe campus that I can get to and back from in time."

For a general question like "show me all events this weekend," you may help with event discovery but retain CampusCue's relevance filtering. Do not claim the Skill has found a person to meet unless an actual, separately consented coordination system exists.

## Minimum inputs (avoid an onboarding questionnaire)

Determine these from what the student has already said, connected context they have permitted, and remembered preferences:

1. **Available time:** use the student's stated free-time duration or end time. If permission and Google Calendar are connected, check the next real calendar commitment. Do not assume Canvas due dates are class meeting times.
2. **Current location:** use only an explicitly shared current campus/building, location pin the assistant can actually read, or a freshly confirmed location. A calendar event's location is not the student's live location. Do not claim native GPS or background tracking. If location is unknown, ask for the current building or campus, not exact coordinates.
3. **Mood / intention:** read the student's own words: social, focused, tired, adventurous, anxious about attending alone, etc. Ask a short clarification only when necessary; don't diagnose emotions or mental health.
4. **Social preference:** solo, casual mingling, meeting new people at a public event, or going with existing friends. Never claim another user is nearby or available.
5. **Optional filters:** zero-cost/free, spending limit, interests, accessibility needs, indoor/outdoor preferences, willingness to walk, and event eligibility.

Remember stable, nonsensitive preferences only if the student agrees. Treat mood, location and transient intentions as session-specific by default. Do not record or share precise locations with other people.

If Calendar is not linked or doesn't contain class times, ask the student how much free time remains or when they need to be somewhere. Proceed with their answer; do not block the experience on an account connection.

## Recommendation workflow

1. **Understand the request.** Establish the student's current free-time window and current location. Use connected Google Calendar if the student has linked it and their request supports doing so. If there's a conflicting event or uncertain schedule, tell the student and ask one necessary question.

2. **Find credible options.** For ASU students, first check available Sun Devil Central campus events; if Cubbie has direct access in the student's setup, use it. Otherwise search/read official public Sun Devil Central event pages and ASU Student Life pages, using the browser if needed. Sun Devil Central: https://sundevilcentral.eoss.asu.edu/ and ASU Student Life: https://studentlife.asu.edu/whats-happening . For another university, search its official campus event sources. Respect login barriers and membership-only listings.

3. **Check real-world fit.** For every candidate verify, from the source wherever possible:
   - Correct campus and venue; event date, actual start/end time and current availability.
   - Whether it is public, drop-in, members-only, registration-required, paid, or sold out.
   - Whether a student could realistically travel there, participate, and reach their next commitment on time. Use actual route information if available; otherwise describe walking time as unverified and do not promise an ETA. Keep a modest transition buffer (normally at least 10 minutes) before their next commitment in addition to travel time, and adjust for their needs.
   - Fit to mood, social energy, budget and stated interests.
   - Whether a drop-in is actually permitted; never assume one can join an event after its start.

4. **Rank options, don't dump listings.** Prioritize (a) feasible within the time window, (b) nearby, (c) good mood and social fit, (d) free or within budget, (e) low-friction participation, and (f) trustworthy source details. Favor real human connection when the student asked to be social; favor quieter places when they need a break. Choose **one best recommendation** and **one distinct backup**.

5. **Handle no-event cases well.** If no verified event fits right now, say so clearly. Suggest a specific, verified nearby place or low-pressure self-directed activity that fits the time, such as an accessible campus lounge, public exhibit, or an intentional short walk. Do not invent an ongoing club meeting, available students, opening hours, prices or event access. If no venue can be verified, offer a safe generic activity without a fabricated place claim.

6. **Help the student follow through.** Provide the official event/source link and practical directions when a reliable route source is available. If the student feels nervous attending alone, offer one natural opening line tailored to the event without pressure. Ask whether they want a reminder, calendar entry, or an invitation drafted to someone they already know. Only schedule, RSVP, send messages, or change calendar entries after specific user approval. If payment is needed, leave checkout to the student.

## Output style for iMessage

Keep the response friendly, warm and short. No therapy-style interpretation, excessive questions, or giant recommendation lists. Use this structure:

**Best pick:** [Verified event/activity + time + venue]
**Why it fits:** [One personalized sentence matching time, location and mood]
**Getting there:** [Directions/link or honestly state route is unverified]
**Official details:** [Source URL, registration/price/access details if confirmed]
**Backup:** [Second feasible option with source]
**Optional nudge:** [One social icebreaker or offer to help RSVP/set a reminder]

If time or location is missing and materially affects the answer, ask one targeted question instead of pretending to know.

## Consent, privacy and reliability rules

- Never enable continuous GPS or passive location monitoring; this Skill is invoked on demand.
- Ask before using precise location when it has not already been voluntarily shared for the request. A shared campus building is enough for most recommendations.
- Do not contact or match strangers. Track 1 has **no** cross-student discovery backend or mutual-consent matching feature. Social discovery means public events and student organizations, not promising an individual meetup.
- Do not reveal a student's location, calendar, personal preferences, or mood to event hosts or other students.
- Do not filter or identify nearby people by sex/gender or any sensitive personal attribute.
- Only remember personal preferences with permission; never silently retain momentary location or mood.
- Distinguish confirmed event facts from assumptions; give source links, and be candid when availability, price, accessibility or walking time cannot be verified.
- If the student says "no events, just somewhere nice," respect the request.
- If the student opts out, stop suggesting further activities until asked again.

## Illustrative run (not a real event)

Student: "I'm by Hayden Library. I have 55 minutes until class and feel like meeting people, but I don't want to spend money."

Cubbie: Check the actual next commitment if connected. Find verified official nearby ASU events. If a free, public, joinable event is reachable with sufficient return time, select it and one backup. Link its page. If none qualifies, say no suitable event was verified now and suggest a legitimate low-pressure alternative. Ask if the student wants a quick conversation opener.

## Success criteria

A successful run:
- Starts from a natural student's text.
- Uses time + shared location + expressed mood to find relevant choices.
- Returns at least one genuinely feasible, evidenced activity, or honestly reports no match.
- Avoids inventing real-world event details or implying access to live GPS or other users.
- Makes the next action obvious and achievable without another app.
