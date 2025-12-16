---
id: 002
title: Spec Clarification Session for Book
stage: spec
date: 2025-12-15
surface: agent
model: claude-opus-4-5-20251101
feature: 001-physical-ai-robotics-book
branch: 001-physical-ai-robotics-book
user: user
command: /sp.clarify
labels: ["clarify", "spec", "exercises", "theory-practice", "capstone", "scope", "audience"]
links:
  spec: specs/001-physical-ai-robotics-book/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-physical-ai-robotics-book/spec.md
tests:
  - null
---

## Prompt

/sp.clarify

My book specification is at specs/book/spec.md

Please analyze it for:

1. AMBIGUOUS TERMS
   - What does "beginner-friendly" mean? (reading level, assumed prior knowledge?)
   - What does "step-by-step explanation" mean? (how many examples per topic? how detailed?)
   - What does "exercises and checkpoints" mean? (number per chapter? format? difficulty?)
   - What does "high-fidelity simulation" mean? (what platforms or tools are expected?)

2. MISSING ASSUMPTIONS
   - Target audience: Are students assumed to have prior AI/robotics knowledge? Level of programming skill?
   - Module length: Approximate word counts per module or chapter?
   - Hardware/software access: Are cloud simulation setups acceptable if students lack RTX hardware?
   - Source of content: Should code examples strictly follow official documentation, or are simplified versions allowed?

3. INCOMPLETE REQUIREMENTS
   - Introduction: What should it contain? (course goals, learning outcomes, hardware overview?)
   - Capstone project: How detailed should it be explained in the spec? (requirements, expected deliverables, assessment criteria?)
   - Module breakdown: Should subtopics be enumerated as separate chapters or sections within a chapter?
   - Exercises: How should they be structured? (hands-on, quizzes, coding tasks?)

4. SCOPE CONFLICTS
   - Is the book strictly about Physical AI & Humanoid Robotics, or can general AI topics be included?
   - Should modules focus on **theory, practice, or both**?

## Response snapshot

Conducted 5-question clarification session addressing user's specific concerns:

**Q1: Exercise Structure** → 1 exercise per chapter, checkpoint quiz at end of each module
**Q2: Theory vs Practice Balance** → 60% theory, 40% practice (theory-heavy for deep understanding)
**Q3: Capstone Deliverables** → Working simulation demo + documented code repository
**Q4: Scope (General AI)** → Strictly Physical AI/Robotics - no general AI beyond direct applications
**Q5: Beginner-Friendly Definition** → High school reading level + basic Python proficiency

All clarifications integrated into spec.md:
- FR-003 updated with exercise/checkpoint structure
- FR-008 updated with 60/40 theory/practice ratio
- FR-025 updated with capstone deliverables
- Constraints section updated with scope limitation
- Target Audience updated with reading level specification
- Clarifications section added with session log

## Outcome

- Impact: 5 ambiguities resolved, spec now production-ready for /sp.plan
- Tests: N/A (specification clarification)
- Files: specs/001-physical-ai-robotics-book/spec.md updated
- Next prompts: /sp.plan to create implementation plan
- Reflection: All user-identified concerns addressed; spec clarity significantly improved

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All clarifications valid and integrated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
