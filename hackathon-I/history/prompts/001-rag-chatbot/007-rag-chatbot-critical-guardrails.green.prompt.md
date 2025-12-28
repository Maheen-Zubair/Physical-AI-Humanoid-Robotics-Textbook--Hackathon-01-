---
id: 007
title: RAG Chatbot Critical Guardrails Implementation
stage: green
date: 2025-12-23
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: developer
command: /sp.tasks
labels: ["selection-mode", "guardrails", "streaming", "qdrant", "versioning", "frontend"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - chatbot/app/services/agent_service.py
  - chatbot/app/services/streaming_service.py
  - chatbot/app/services/vector_store.py
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.css
  - specs/001-rag-chatbot/tasks.md
tests:
  - null
---

## Prompt

/sp.tasks update You are continuing implementation based on the existing tasks.md for the Integrated RAG Chatbot. Your task is to IMPLEMENT the remaining critical improvements from the updated plan and task list.

## Objectives
1. **Selection-Mode Guardrail (CRITICAL)**: Add hard system instruction to selection mode forbidding external knowledge. If the answer is not in the selected text, respond with "This information is not present in the selected text."
2. **Streaming Fallback Logic (CRITICAL)**: Implement safe fallback when Gemini streaming is unavailable, times out, or errors. Automatically fall back to non-streaming. Log fallback events.
3. **Qdrant Collection Versioning (Recommended)**: Add versioned collections (e.g., book_chunks_v2) with aliasing.
4. **Frontend UX Mode Indicator (Recommended)**: Add visible badge showing "Answering from selected text only" or "Answering from book content".

## Constraints
- Strictly use Context7 MCP for all library documentation lookups.
- Do NOT refactor or change unrelated code. Keep changes additive and minimal.
- Update tasks.md ONLY if strictly required by new implementation.

## Response snapshot

Successfully implemented all 4 critical improvements for the RAG Chatbot:

### 1. Selection-Mode Guardrail (CRITICAL) - agent_service.py
- Added `SELECTION_MODE_SYSTEM_PROMPT` constant with hard guardrail forbidding external knowledge
- Added `RETRIEVAL_MODE_SYSTEM_PROMPT` constant for book content retrieval
- Added `_get_system_prompt()` method to select appropriate prompt based on mode
- Updated `generate_response()` to use the new SDK pattern with `google.genai`
- System prompt explicitly states: "If the answer is not present in the selected text, you MUST respond EXACTLY with: 'This information is not present in the selected text.'"

### 2. Streaming Fallback Logic (CRITICAL)
- Created new `streaming_service.py` with `StreamingService` class
- Added `StreamingStatus` enum (STREAMING, FALLBACK, ERROR, COMPLETE)
- Added `StreamingConfig` dataclass for timeout/retry configuration
- Implemented `stream_with_fallback()` method with automatic fallback
- Added `generate_response_stream()` in agent_service.py with timeout protection
- Added `_fallback_to_non_streaming()` method for graceful degradation
- All fallback events are logged with structured logging

### 3. Qdrant Collection Versioning (Recommended) - vector_store.py
- Added versioning constants: `CURRENT_VERSION = "v2"`, `VECTOR_DIMENSIONS = 1024`
- Added `versioned_collection_name` property returning `book_embeddings_v2`
- Added `active_collection_name` property for alias-aware querying
- Implemented `_setup_alias()` for transparent version switching
- Added `create_new_version()` method for migration purposes
- Added `switch_alias_to_version()` method for seamless upgrades
- Added `list_versions()` method to enumerate available versions

### 4. Frontend UX Mode Indicator (Recommended)
- Updated ChatWidget.jsx to track `responseMode` in bot messages
- Added mode indicator badge with conditional rendering
- Shows "Answering from selected text only" for selection mode
- Shows "Answering from book content" for retrieval mode
- Added CSS styles for `.mode-indicator`, `.mode-selection`, `.mode-retrieval`
- Added responsive styles for mobile displays

### Tasks Updated
- Added Phase 12 with 14 new tasks (T087-T100), all marked complete
- Updated task summary table to reflect 100 total tasks

## Outcome

- Impact: Critical guardrails implemented preventing hallucinations in selection mode; streaming now has automatic fallback; Qdrant collections support versioning for future migrations; frontend clearly indicates response source
- Tests: Manual testing required - selection mode should respond "This information is not present in the selected text" for out-of-context questions
- Files: 6 files modified (agent_service.py, streaming_service.py, vector_store.py, ChatWidget.jsx, ChatWidget.css, tasks.md)
- Next prompts: Implement POST /chat/stream endpoint (T074), test streaming with browser EventSource
- Reflection: Using Context7 for google-genai SDK patterns was essential for correct streaming implementation

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation; all changes were additive
- Graders run and results (PASS/FAIL): Not applicable (implementation phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy and test selection-mode guardrail with out-of-context questions to verify hard guardrail effectiveness
