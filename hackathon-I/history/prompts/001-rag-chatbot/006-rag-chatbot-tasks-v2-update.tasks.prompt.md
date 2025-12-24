---
id: 006
title: RAG Chatbot Tasks v2 Update
stage: tasks
date: 2025-12-23
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: user
command: /sp.tasks update
labels: ["rag", "chatbot", "tasks", "streaming", "v2", "api"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/tasks.md
tests:
  - null
---

## Prompt

/sp.tasks update

## Response snapshot

Updated tasks.md with Phase 11: v2 Enhancements (15 new tasks T072-T086):

**New Tasks Added:**

1. **Streaming Support (T072-T075)**:
   - SSE streaming generator utility
   - Gemini 2.5 Flash streaming wrapper
   - POST /chat/stream endpoint
   - Frontend streaming response handling

2. **Explicit Selected-Text Endpoint (T076-T077)**:
   - POST /selected-text-query implementation
   - SelectedTextRequest validation model

3. **Health Check Updates (T078-T079)**:
   - Cohere service status in health endpoint
   - Cohere API ping utility

4. **Frontend v2 Updates (T080-T082)**:
   - Streaming mode toggle in ChatWidget
   - Progressive text rendering
   - SSE connection retry logic

5. **Integration & Validation (T083-T086)**:
   - CORS configuration for streaming
   - Endpoint testing
   - Documentation updates

**Summary:**
- v1 Complete: 71 tasks (T001-T071) all marked ✅
- v2 New: 15 tasks (T072-T086) added for streaming and new endpoints
- Total: 86 tasks

Updated Context7 checkpoints with Gemini streaming and FastAPI SSE references.

## Outcome

- ✅ Impact: tasks.md updated with v2 enhancement tasks for streaming and new API endpoints
- 🧪 Tests: No tests (task generation phase)
- 📁 Files: 1 file updated (tasks.md)
- 🔁 Next prompts: Begin implementation with T072 (SSE streaming generator)
- 🧠 Reflection: v2 tasks build on completed v1 foundation; streaming support aligns with api-spec.yaml v2.0.0

## Evaluation notes (flywheel)

- Failure modes observed: None - incremental update to existing tasks.md
- Graders run and results (PASS/FAIL): N/A (task generation phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement T072 first to establish streaming pattern for other tasks
