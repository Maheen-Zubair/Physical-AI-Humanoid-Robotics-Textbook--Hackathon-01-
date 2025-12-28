---
id: 011
title: CORS Failed to Fetch Fix
stage: misc
date: 2025-12-24
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: system
command: /sp.analyze
labels: ["cors", "networking", "debugging", "frontend"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - chatbot/app/main.py
tests:
  - curl OPTIONS preflight test
  - Browser testing
---

## Prompt

/sp.analyze Observed issue:
When a user submits any query, the chatbot responds with:
"Failed to fetch"

## Response snapshot

### Root Cause Analysis

**Primary Issue:** CORS preflight requests returning 400 Bad Request

Backend logs showed:
```
OPTIONS /api/chat/stream HTTP/1.1" 400 Bad Request
OPTIONS /api/chat HTTP/1.1" 400 Bad Request
```

**Why "Failed to fetch":**
1. Browser sends OPTIONS preflight request before actual POST
2. CORS middleware configuration had issues:
   - `allow_origin_regex` conflicting with `allow_origins`
   - Rate limiter middleware potentially interfering
3. OPTIONS returning 400 caused browser to abort the actual request

### Fixes Applied

1. **Removed `allow_origin_regex`** - Was conflicting with `allow_origins`

2. **Added explicit localhost origins**:
   ```python
   dev_origins = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "http://localhost:8001",
       "http://127.0.0.1:8001",
   ]
   ```

3. **Skip OPTIONS in rate limiter**:
   ```python
   if request.method == "OPTIONS":
       response = await call_next(request)
       return response
   ```

4. **Added all HTTP methods**:
   ```python
   allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
   ```

### Verification

```bash
curl -X OPTIONS http://localhost:8001/api/chat/stream \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"
```

Response:
```
HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:3000
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, HEAD
```

## Outcome

- Impact: CORS preflight now returns 200 OK with correct headers
- Tests: curl OPTIONS test passed
- Files: 1 file modified (main.py)
- Next prompts: Test in browser to confirm fix
- Reflection: CORS issues are common with SSE streaming; must allow OPTIONS method explicitly

## Evaluation notes (flywheel)

- Failure modes observed: CORS middleware misconfiguration, allow_origin_regex conflicting
- Graders run and results (PASS/FAIL): PASS - curl test shows 200 OK
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Test actual chat request in browser
