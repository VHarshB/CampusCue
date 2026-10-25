
# CampusCue — Make Your Gap Count

**Cubbie Hackathon | Track 1 | Arizona State University**

CampusCue transforms free time between classes into personalized campus experiences.

Instead of immediately showing students a list of events, Cubbie first understands how they're feeling, what they want to do, and how much time they have.

Then it recommends something worthwhile, nearby, and realistic.

> **Our goal:** Make Cubbie feel like a thoughtful campus friend who understands your mood before suggesting what to do.

## The Problem

Students frequently have unexpected free time between classes.

Campus is full of events, organizations, activities, and interesting places, but finding something relevant at the right moment can be frustrating.

Traditional campus event platforms show what's happening.

They don't necessarily understand:

- How a student feels
- What they actually want
- How much time they have
- Where they currently are
- Whether attending an event is practical

CampusCue bridges this gap.

## Our Solution

CampusCue is a conversational campus discovery Skill built for Cubbie.

It combines:

**Mood + Intention + Time + Location**

to recommend one useful campus activity.

The main innovation isn't simply finding events.

It's understanding the student before making a suggestion.

## How It Works

### Step 1 — Understand the Student

Student:
"Cubbie, I'm bored. What should I do?"

Cubbie:
"What's your mood right now—social, chill, or adventurous? And what do you feel like doing?"

CampusCue starts with a natural conversation rather than immediately generating recommendations.

### Step 2 — Understand Their Situation

Student:
"Feeling social! I want to meet new people."

Cubbie:
"Nice! How much time do you have, and where on campus are you?"

CampusCue asks only for missing information.

If the student already gave their time, location, mood, or goal, it doesn't ask again.

### Step 3 — Find a Suitable Activity

CampusCue checks relevant official campus sources and evaluates:

- Mood and interests
- Available time
- Current campus area
- Event timing and location
- Registration requirements
- Budget
- Whether attending is actually feasible

### Step 4 — Recommend Something Useful

CampusCue returns:

- One best recommendation
- A brief reason it fits
- Verified time/location details when relevant
- An official event link
- One backup only when useful

Responses are short, friendly, and conversational.

If no suitable event can be verified, Cubbie provides an honest, practical alternative.

**Note:** The examples illustrate intended conversation behavior, not live verified event results.

## Key Features

### 1. Mood-First Discovery

CampusCue learns how the student feels before recommending an experience.

Different moods lead to different suggestions.

For example:

| Student mood | Suitable experiences |
|---|---|
| Social | Public events, student organizations, casual gatherings |
| Relaxed | Quiet areas, peaceful outdoor activities |
| Productive | Study spots, workshops, learning opportunities |
| Adventurous | New places, exhibitions, interesting events |
| Tired | Low-effort breaks and comfortable spaces |

The student always controls what kind of experience they want.

### 2. Personalized Conversation

CampusCue doesn't use a rigid questionnaire.

It asks one or two short questions when important information is missing.

It avoids repeating questions the student has already answered.

When enough context exists, it moves directly to a recommendation.

### 3. Time-Aware Suggestions

CampusCue considers the student's available free time.

If Google Calendar is connected and access is authorized, it can use relevant calendar information.

Otherwise, it simply asks how much time remains.

Suggestions should leave reasonable time to return to the next commitment.

### 4. Location-Aware Discovery

CampusCue uses the student's voluntarily shared campus or building.

It does not assume access to live GPS.

Activities should be realistically accessible from the student's location.

### 5. Real Campus Sources

For ASU, CampusCue prioritizes:

- [Sun Devil Central](https://sundevilcentral.eoss.asu.edu/)
- [ASU Events](https://events.asu.edu/)
- [ASU Student Life](https://studentlife.asu.edu/whats-happening)

Events should be verified whenever possible before being recommended.

A public website does not automatically mean Cubbie has a native integration with it.

### 6. Short, Human Responses

CampusCue should feel natural through iMessage.

Target lengths:

- Discovery questions: 15–35 words
- Recommendations: 25–55 words, excluding links

No large event lists, robotic templates, unnecessary explanations, or repetitive follow-up questions.

## MVP Scope — Track 1

The first version focuses on:

1. Activating from natural student messages.
2. Asking about mood and desired activity when unknown.
3. Collecting essential time and location context.
4. Finding relevant campus events and activities.
5. Checking feasibility using available information.
6. Returning one concise, personalized recommendation.
7. Handling situations where no suitable event exists.

### Out of Scope

CampusCue Track 1 does not claim to provide:

- Continuous GPS tracking
- Automatic background recommendations
- Nearby student identification
- Direct student-to-student matching
- Guaranteed introductions
- An independent mobile application or backend

These are not required for this Skill.

## Repository Structure

```text
CampusCue/
├── README.md
├── SKILL.md
└── TEST_PLAN.md
```

**README.md:** Project overview, behavior, development, and demo guidance.

**SKILL.md:** Cubbie's actual conversation and recommendation instructions.

**TEST_PLAN.md:** Test scenarios, expected behavior, and release checks.

## Team Development Plan

Work can be divided into parallel responsibilities.

| Workstream | Responsibility |
|---|---|
| Repository & Integration | Manage repository, issues, collaboration, Skill installation, and submission |
| Skill Behavior | Improve mood-first interaction, follow-ups, personalization, and concise responses |
| Event Discovery | Investigate official campus sources and verify activity feasibility |
| Testing & Reliability | Test real Cubbie replies, edge cases, and unsupported capabilities |
| Demo & Video | Record a clear, engaging demonstration using authentic Cubbie behavior |

These are workstreams, not necessarily separate registered team members. Follow the hackathon's current team-size rules.

### Collaboration Guidelines

1. Create a GitHub Issue for each workstream.
2. Assign responsibilities clearly.
3. Use separate branches when working concurrently.
4. Submit changes through pull requests.
5. Test the Skill before merging or releasing.
6. Avoid committing private student information or account credentials.

## Testing

The Skill must be tested on a real Cubbie account before its behavior is described as verified.

See [TEST_PLAN.md](TEST_PLAN.md).

### Critical Scenarios

**Test 1: Unknown Mood**

Message:
"I'm bored. What should I do?"

Expected:
Cubbie asks about mood and desired experience before suggesting events.

**Test 2: Mood Already Provided**

Message:
"I'm feeling social and want to meet people."

Expected:
Cubbie asks only for missing information, such as time and campus location.

**Test 3: Complete Context**

Message:
"I'm near Hayden, have 45 minutes, and want a free social event."

Expected:
Cubbie proceeds directly to finding a suitable activity without unnecessary questions.

**Test 4: Short Responses**

Expected:
Cubbie replies naturally and concisely without producing a lengthy event report.

**Test 5: No Verified Events**

Expected:
Cubbie explains that no suitable event was verified and provides a practical alternative.

**Test 6: Privacy**

Expected:
Cubbie never invents GPS access, nearby students, or access to private information.

### Release Requirements

- Skill installs successfully.
- Mood-first conversation works.
- Already supplied information is not repeatedly requested.
- Recommendations fit stated constraints.
- Event facts are verified where possible.
- Replies are concise.
- No unavailable capabilities are claimed.
- Real-account tests and observed results are documented.

## Demo Video — 58-Second Concept

The demo should communicate how CampusCue transforms a student's free time into a personalized experience.

| Time | Visual | Narration |
|---|---|---|
| 0–7 sec | Student finishes class with 45 minutes free | "Ever have time between classes and absolutely no idea what to do?" |
| 7–14 sec | Student scrolls through overwhelming event listings | "There's so much happening on campus, but what's actually for you?" |
| 14–22 sec | Student texts Cubbie | "So I asked Cubbie." |
| 22–32 sec | Cubbie asks about mood and what the student wants | "Instead of throwing events at me, it first understands how I'm feeling." |
| 32–43 sec | Authentic concise recommendation appears with official source | "Then it finds something that actually fits my time, mood, and location." |
| 43–52 sec | Student follows through on the suggestion | "Less scrolling, and more time actually doing something." |
| 52–58 sec | Campus activity and CampusCue end card | "CampusCue. Make your gap count." |

Use genuine Cubbie output for the product demonstration.

Staged campus lifestyle footage is acceptable, but it should not be represented as evidence of a real event recommendation.

If no real event qualifies, demonstrate the honest fallback behavior instead.

## Installation

1. Keep this GitHub repository public.
2. Ensure `SKILL.md` exists in the repository root.
3. Open your Cubbie iMessage conversation.
4. Share the GitHub repository URL.
5. Follow the Skill installation prompts and approve installation.
6. Test using the scenarios above.

Repository:

https://github.com/VHarshB/CampusCue

### Updating an Installed Skill

After modifying `SKILL.md`, request a CampusCue update in Cubbie and approve the new version.

Installed versions may be pinned to an earlier GitHub commit.

Always confirm the latest version is installed before testing.

## Submission

Before final submission:

1. Verify the Skill installs and activates.
2. Test the mood-first discovery flow.
3. Verify concise, personalized recommendations.
4. Document results from an actual Cubbie account.
5. Record the tested GitHub commit.
6. Include authentic demonstration evidence.
7. Follow the official hackathon submission requirements and deadlines.

Official hackathon:

https://hackathon.cubbie.ai/

## References

- [Cubbie Hackathon](https://hackathon.cubbie.ai/)
- [Official Cubbie Hackathon Kit](https://github.com/imaginix-inc/cubbie-hackathon-kit)
- [Cubbie Skill Guide](https://hackathon.cubbie.ai/skill.md)
- [ASU Sun Devil Central](https://sundevilcentral.eoss.asu.edu/)
- [ASU Events](https://events.asu.edu/)
- [ASU Student Life](https://studentlife.asu.edu/whats-happening)

## Our Vision

CampusCue isn't about recommending more events.

It's about making campus life feel more accessible, personal, and spontaneous.

Sometimes students want to meet people.

Sometimes they want to explore.

Sometimes they just need a quiet break.

**CampusCue understands the difference.**

**Make Your Gap Count.**
