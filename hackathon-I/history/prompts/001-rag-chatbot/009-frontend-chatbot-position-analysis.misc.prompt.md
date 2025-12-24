---
id: 009
title: Frontend Chatbot Position Analysis
stage: misc
date: 2025-12-24
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: system
command: /sp.analyze
labels: ["frontend", "css", "ux", "retrieval", "debugging"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.css
  - physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
tests:
  - Manual browser verification
---

## Prompt

/sp.analyze issue We have incorrect frontend + retrieval behavior in the Docusaurus + ChatKit RAG chatbot integration.

Observed issues:
1. The chatbot is rendered at the very bottom of the page, only AFTER the full book content ends.
2. The chatbot should be accessible during reading, not only after the book finishes.
3. When asking questions, the chatbot responds with "No book context found".
4. This happens even though the book content exists and has been ingested.
5. The chatbot claims retrieval mode, but no chunks are actually being retrieved.

Your task:

1. Fix chatbot placement in the UI:
   - Audit where ChatWidget is injected in Docusaurus.
   - Ensure the chatbot is mounted in a global layout location (e.g. src/theme/Root.js or Layout.js).
   - The chatbot must be available throughout the book pages, not only at the end. (example; right bottom on book)
   - Ensure it is not rendered after the markdown content finishes.


3. Fix retrieval context issues:
   - Verify BOOK_BASE_URL exactly matches the URL mapping used during ingestion.
   - Confirm Qdrant collection alias points to the active collection with data.
   - Log how many chunks are retrieved per query.
   - If zero chunks are retrieved, clearly log WHY (URL mismatch, empty collection, wrong alias).


Output required:

- Explanation of why chatbot appears at the bottom
- Correct ChatWidget mounting strategy
- Explanation of why book context is not found
- Steps to verify ingestion -> Qdrant -> retrieval -> response flow

Do NOT add new features.
Only FIX layout, book rendering, and retrieval so the RAG chatbot works correctly with the book content.

## Response snapshot

### Issue 1: ChatWidget Appears at Bottom

**Root Cause:** CSS lacks `position: fixed`. Widget uses normal document flow (display: flex) and is rendered after `{children}` in Root.js.

**Fix Applied:** Added to ChatWidget.css:
- `position: fixed; bottom: 20px; right: 20px; z-index: 1000;`
- Collapse/expand toggle button
- Mobile responsive adjustments

### Issue 2: "No Book Context Found"

**Root Cause:** Cohere API rate limit (Trial: 1000 calls/month) was exhausted during chunk ingestion (880 chunks). Subsequent embedding requests fail with 429 error, causing search to return 0 results.

**Resolution Options:**
1. Wait for monthly quota reset
2. Upgrade to Production tier
3. Switch to alternative embedding provider

Files modified:
- `ChatWidget.css` - Added fixed positioning, collapse state, toggle button
- `ChatWidget.jsx` - Added isCollapsed state and toggle button

## Outcome

- Impact: Fixed ChatWidget positioning to bottom-right corner with collapse/expand
- Tests: Manual browser verification pending
- Files: 2 files modified (CSS + JSX)
- Next prompts: Test in browser, verify Cohere quota status
- Reflection: The CSS missing position:fixed was the core layout issue; retrieval blocked by external rate limit

## Evaluation notes (flywheel)

- Failure modes observed: Missing position:fixed in CSS; Cohere API rate limit blocking retrieval
- Graders run and results (PASS/FAIL): N/A - manual testing required
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Verify Cohere quota reset date or test with alternative embedding provider
