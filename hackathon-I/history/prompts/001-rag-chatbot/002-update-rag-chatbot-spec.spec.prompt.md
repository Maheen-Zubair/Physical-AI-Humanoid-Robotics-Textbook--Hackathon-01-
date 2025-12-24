---
id: 002
title: Update RAG Chatbot Specification with Architecture
stage: spec
date: 2025-12-17
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: system
command: /sp.specify
labels: ["rag", "chatbot", "specification", "architecture-update", "hackathon"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/spec.md
  - specs/001-rag-chatbot/checklists/requirements.md
tests:
  - none
---

## Prompt

update 001-rag-chatbot/spec.md file Update the specification at specs.md to establish the correct technical architecture and logic for the Integrated RAG Chatbot. Ensure all sections (Requirements, Assumptions, Dependencies) are rewritten to match this specific hackathon workflow:

Core Tech Stack & Roles:
- Orchestration: OpenAI Agents SDK (Backend) & OpenAI ChatKit (Frontend UI)
- Embedding Model: Gemini API (models/embedding-001) for all vector generation
- Vector Store: Qdrant Cloud Free Tier (stores Gemini vectors)
- Metadata Store: Neon Serverless Postgres (stores raw book text, chapter titles, and Docusaurus URLs)
- Backend: FastAPI hosted on Hugging Face Spaces (Docker, Port 7860)
- Frontend: Docusaurus site hosted on GitHub Pages

Refined Chat Logic (Selection vs. Search):
- The "Selected Text" Rule: If the user has highlighted text, the ChatKit UI MUST send this text as a context_selection payload. The FastAPI backend MUST use ONLY this text for grounding the answer, bypassing the Qdrant search entirely.
- General Search: If no text is selected, the system generates a Gemini embedding for the query → performs a similarity search in Qdrant → fetches the full text and URL from Neon → generates the answer via OpenAI.

Missing Features & Ambiguities:
- Ingestion Script: Add a requirement for a Python script that parses Docusaurus Markdown, chunks content by headers, generates Gemini embeddings, and populates both Neon (SQL) and Qdrant (Vector).
- Reference Format: Chatbot responses must use Markdown links for citations: [Source: Chapter Name](https://your-site.io/docs/link).
- CORS Policy: Backend must explicitly permit requests from the GitHub Pages domain.

Success Criteria & Outcomes:
- SC-001: 100% adherence to "Selected Text" constraint when context is provided.
- SC-002: End-to-end response time under 3 seconds

## Response snapshot

Updated the existing 001-rag-chatbot specification with refined architecture:

**Key Changes Made:**
1. User Story 2 (Selected Text) - Strengthened to "ONLY" constraint, no vector search when selection present
2. Added User Story 5 - Content Ingestion workflow for book updates
3. Expanded FR-001 to FR-020 with clear categorization:
   - Core Chat Functionality (FR-001 to FR-005)
   - Selected Text Behavior - Strict Constraint (FR-006 to FR-008)
   - Semantic Search Behavior (FR-009 to FR-011)
   - Out-of-Scope Handling (FR-012 to FR-013)
   - Content Ingestion (FR-014 to FR-017)
   - Cross-Origin & Integration (FR-018 to FR-020)
4. Updated Success Criteria:
   - SC-001: 100% selected text adherence
   - SC-002: 3 second response time
   - Added SC-008 for ingestion completeness
5. Added Technical Constraints section for hackathon requirements
6. Updated Dependencies with Neon Postgres, OpenAI Agents SDK, OpenAI ChatKit
7. Added edge cases for empty selection and degraded metadata store

## Outcome

- ✅ Impact: Specification refined with clear dual-mode logic (selection vs search) and hackathon constraints
- 🧪 Tests: Quality checklist re-validated - all 16 items pass
- 📁 Files: 2 files updated (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.clarify or /sp.plan to proceed with implementation planning
- 🧠 Reflection: User provided detailed technical architecture; documented as dependencies/constraints while keeping functional requirements technology-agnostic

## Evaluation notes (flywheel)

- Failure modes observed: None - comprehensive input allowed smooth update
- Graders run and results (PASS/FAIL): Manual checklist validation - PASS
- Prompt variant (if applicable): Update variant (not new feature)
- Next experiment (smallest change to try): N/A - specification update complete
