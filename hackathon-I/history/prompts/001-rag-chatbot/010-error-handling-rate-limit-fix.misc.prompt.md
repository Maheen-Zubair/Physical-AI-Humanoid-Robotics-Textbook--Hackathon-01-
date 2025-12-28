---
id: 010
title: Error Handling Rate Limit Fix
stage: misc
date: 2025-12-24
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: system
command: /sp.analyze
labels: ["error-handling", "rate-limit", "cohere", "debugging", "ux"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - chatbot/app/exceptions.py
  - chatbot/app/services/embedding_service.py
  - chatbot/app/routers/chat.py
  - chatbot/app/models/chat_response.py
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.css
tests:
  - Backend restart verification
  - Manual browser testing
---

## Prompt

/sp.analyze fix the error:
When a user asks any question, the chatbot responds with:
"Sorry, I encountered an error processing your request. Please try again."

This appears to be a generic runtime error, not a UI or content issue.

Required Investigation:
Identify all possible failure points in the query-handling pipeline:
frontend -> API route -> RAG orchestrator -> vector store -> LLM call
...

## Response snapshot

### Root Cause Analysis

**Primary Issue:** Cohere API rate limit (HTTP 429)

The backend logs clearly showed:
```
HTTP Request: POST https://api.cohere.com/v1/embed "HTTP/1.1 429 Too Many Requests"
"You are using a Trial key, which is limited to 1000 API calls / month"
```

**Error Flow:**
1. User sends query (retrieval mode)
2. `embedding_service.embed_text()` calls Cohere API
3. Cohere returns 429 Rate Limit Error
4. Exception propagates up to chat router
5. Generic error message returned to frontend

### Fixes Applied

1. **Created `app/exceptions.py`** - Custom exception classes:
   - `ChatbotException` (base class)
   - `RateLimitError` - for API rate limits
   - `EmbeddingError` - for embedding failures
   - `LLMError` - for LLM generation failures

2. **Updated `embedding_service.py`**:
   - Detects 429 rate limit errors specifically
   - Raises `RateLimitError` with user-friendly message
   - Provides actionable suggestion (use selection mode)

3. **Updated `chat.py` router**:
   - Added `get_user_friendly_error()` helper function
   - Catches `ChatbotException` separately from generic exceptions
   - Returns structured error response with error_code

4. **Updated `ChatResponse` model**:
   - Added `error_code` optional field

5. **Updated frontend `ChatWidget.jsx`**:
   - Extracts user-friendly message from backend
   - Displays actionable error message

6. **Added CSS styling** for rate limit errors

### User-Friendly Error Message

Before: "Sorry, I encountered an error processing your request. Please try again."

After: "The Cohere API rate limit has been reached. This is a temporary issue. Please try again in a few minutes, or select text from the book and ask a question about it (selection mode works without embeddings)."

## Outcome

- Impact: Users now see actionable error messages with suggestions
- Tests: Backend restart verified, manual testing pending
- Files: 6 files modified
- Next prompts: Monitor for other error types, consider alternative embedding providers
- Reflection: The generic error was hiding the real issue (rate limit); structured error handling makes debugging easier

## Evaluation notes (flywheel)

- Failure modes observed: Cohere Trial tier 1000 calls/month limit exhausted
- Graders run and results (PASS/FAIL): N/A - manual testing
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add rate limit status to health endpoint; consider caching embeddings
