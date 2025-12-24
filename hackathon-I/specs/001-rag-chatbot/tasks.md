# Tasks: Integrated RAG Chatbot

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/api-spec.yaml ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

```
hackathon-I/
├── chatbot/                      # Backend (FastAPI on HF Spaces)
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Environment configuration
│   │   ├── models/               # Pydantic models
│   │   ├── services/             # Business logic
│   │   ├── routers/              # API endpoints
│   │   └── middleware/           # Rate limiting, CORS
│   ├── ingestion/
│   │   ├── ingest.py             # Main ingestion script
│   │   ├── chunker.py            # Header-based chunking
│   │   ├── embedder.py           # Cohere embedding
│   │   └── url_mapper.py         # File path → URL mapping
│   ├── tests/
│   └── requirements.txt
├── docs/                         # Docusaurus book content (source)
└── src/components/               # Frontend (ChatKit integration)
    └── ChatWidget/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in chatbot/
- [X] T002 Initialize Python project with FastAPI, Qdrant, Cohere dependencies in chatbot/requirements.txt
- [X] T003 [P] Create environment configuration module in chatbot/app/config.py
- [X] T004 [P] Create .env.example with all required environment variables in chatbot/.env.example
- [X] T005 [P] Setup Dockerfile for Hugging Face Spaces deployment in chatbot/Dockerfile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Store Setup

- [X] T006 Create Neon Postgres connection module in chatbot/app/services/database.py
- [X] T007 Create Qdrant client connection module in chatbot/app/services/vector_store.py
- [X] T008 [P] Create book_chunks table schema and migration in chatbot/app/models/book_chunk.py
- [X] T009 [P] Create Qdrant collection configuration (1024 dims, cosine) in chatbot/app/services/vector_store.py

### Core Models & Services

- [X] T010 Create ChatRequest Pydantic model per api-spec.yaml in chatbot/app/models/chat_request.py
- [X] T011 [P] Create ChatResponse Pydantic model per api-spec.yaml in chatbot/app/models/chat_response.py
- [X] T012 [P] Create Source Pydantic model per api-spec.yaml in chatbot/app/models/source.py
- [X] T013 [P] Create ErrorResponse Pydantic model per api-spec.yaml in chatbot/app/models/error_response.py
- [X] T014 Create QueryContext runtime model per data-model.md in chatbot/app/models/query_context.py
- [X] T015 Create ChatSession in-memory model per data-model.md in chatbot/app/models/chat_session.py

### API Foundation

- [X] T016 Create FastAPI app scaffold with CORS middleware in chatbot/app/main.py
- [X] T017 [P] Create health check endpoint (GET /health) in chatbot/app/routers/health.py
- [X] T018 Implement environment validation on startup per plan.md in chatbot/app/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - Content Ingestion (Priority: P3 - but prerequisite) 🔧

**Goal**: Ingest book content into Qdrant + Neon so the chatbot can answer questions

**Independent Test**: Run ingestion on a test chapter, verify chunks appear in both stores, then query for the content

**Why first**: Without ingested content, US1 (retrieval mode) cannot be tested

### Implementation for User Story 5

- [X] T019 [US5] Create markdown parser with frontmatter extraction in chatbot/ingestion/parser.py
- [X] T020 [P] [US5] Create header-based chunker with token fallback in chatbot/ingestion/chunker.py
- [X] T021 [P] [US5] Create URL mapper (file path → deployed URL) in chatbot/ingestion/url_mapper.py
- [X] T022 [US5] Create Cohere embedding generator (context7: cohere) in chatbot/ingestion/embedder.py
- [X] T023 [US5] Create dual-store writer (atomic Qdrant + Neon) in chatbot/ingestion/writer.py
- [X] T024 [US5] Create main ingestion script with CLI interface in chatbot/ingestion/ingest.py
- [X] T025 [US5] Add error handling for ingestion failures (retry, logging) in chatbot/ingestion/ingest.py
- [X] T026 [US5] Ingest full book content from docs/ folder using ingest.py

**Checkpoint**: Ingestion complete - chatbot can now retrieve book content

---

## Phase 4: User Story 1 - Ask Question About Book Content (Priority: P1) 🎯 MVP

**Goal**: Reader asks a question without selection → semantic search → grounded response with citation

**Independent Test**: Ask "What is inverse kinematics?" and verify response includes accurate content from the book with a clickable citation link

### Implementation for User Story 1

- [X] T027 [US1] Create Cohere query embedding service (context7: cohere) in chatbot/app/services/embedding_service.py
- [X] T028 [US1] Create Qdrant similarity search service (context7: qdrant-client) in chatbot/app/services/search_service.py
- [X] T029 [US1] Create Neon metadata lookup service (chunk_id → full text + URL) in chatbot/app/services/metadata_service.py
- [X] T030 [US1] Create context assembly service (combine chunks, respect token budget) in chatbot/app/services/context_service.py
- [X] T031 [US1] Create Google GenerativeAI integration with system prompt (context7: google-generativeai) in chatbot/app/services/agent_service.py
- [X] T032 [US1] Create citation validator (regex check, fallback append) in chatbot/app/services/citation_service.py
- [X] T033 [US1] Create query router (selection vs retrieval detection) in chatbot/app/services/router_service.py
- [X] T034 [US1] Implement POST /chat endpoint for retrieval mode in chatbot/app/routers/chat.py
- [X] T035 [US1] Add conversation session management (in-memory, 30min TTL) in chatbot/app/services/session_service.py
- [X] T036 [US1] Add logging for retrieval flow (embeddings, search, context, response) in chatbot/app/routers/chat.py

**Checkpoint**: User Story 1 complete - retrieval mode is functional and testable

---

## Phase 5: User Story 2 - Ask Question Using Selected Text (Priority: P1) 🎯

**Goal**: Reader selects text + asks question → response uses ONLY selected text (NO vector search)

**Independent Test**: Select a paragraph, ask "Explain this in simpler terms", verify response uses ONLY the selected text and logs show zero Qdrant calls

### Implementation for User Story 2

- [X] T037 [US2] Extend query router to handle context_selection in chatbot/app/services/router_service.py
- [X] T038 [US2] Create selection-mode context assembly (no search, selection only) in chatbot/app/services/context_service.py
- [X] T039 [US2] Add empty/whitespace selection detection with user feedback in chatbot/app/services/router_service.py
- [X] T040 [US2] Extend POST /chat endpoint for selection mode in chatbot/app/routers/chat.py
- [X] T041 [US2] Add logging to confirm zero Qdrant calls when selection present in chatbot/app/routers/chat.py
- [X] T042 [US2] Add selection_ignored flag to response when empty selection detected in chatbot/app/routers/chat.py

**Checkpoint**: User Story 2 complete - selection mode is functional and testable independently

---

## Phase 6: User Story 3 - Handle Out-of-Scope Questions (Priority: P2)

**Goal**: Reader asks question not covered in book → graceful decline with helpful message

**Independent Test**: Ask "What is the stock price of Tesla?" and verify the chatbot declines appropriately without attempting to answer

### Implementation for User Story 3

- [X] T043 [US3] Create similarity threshold detection (< 0.65 = out-of-scope flag) in chatbot/app/services/search_service.py
- [X] T044 [US3] Add LLM guardrail instruction to system prompt for uncertainty detection in chatbot/app/services/agent_service.py
- [X] T045 [US3] Create combined out-of-scope handler (threshold + LLM) in chatbot/app/services/scope_service.py
- [X] T046 [US3] Add out_of_scope flag to ChatResponse in chatbot/app/models/chat_response.py
- [X] T047 [US3] Add related topic suggestions when declining out-of-scope in chatbot/app/services/scope_service.py
- [X] T048 [US3] Update POST /chat endpoint to handle out-of-scope responses in chatbot/app/routers/chat.py

**Checkpoint**: User Story 3 complete - out-of-scope detection is functional

---

## Phase 7: User Story 4 - Access Chatbot on Mobile Device (Priority: P2)

**Goal**: Chatbot interface is usable on mobile devices (320px minimum)

**Independent Test**: Access the chatbot on a 320px viewport and complete a question-answer flow

### Implementation for User Story 4 (Frontend)

- [X] T049 [US4] Create ChatKit wrapper component with selection capture in src/components/ChatWidget/ChatWidget.jsx
- [X] T050 [US4] Implement text selection capture on message submit in src/components/ChatWidget/SelectionCapture.js
- [X] T051 [US4] Create session manager (localStorage for session_id) in src/components/ChatWidget/SessionManager.js
- [X] T052 [US4] Add responsive styling for mobile (320px minimum) in src/components/ChatWidget/ChatWidget.css
- [X] T053 [US4] Integrate ChatWidget into Docusaurus layout in src/theme/Root.js
- [X] T054 [US4] Add mobile text selection gesture support in src/components/ChatWidget/SelectionCapture.js
- [X] T055 [US4] Add loading indicator for cold start scenarios in src/components/ChatWidget/ChatWidget.jsx

**Checkpoint**: User Story 4 complete - chatbot is responsive and mobile-friendly

---

## Phase 8: Hardening & Rate Limiting

**Purpose**: Security, reliability, and free-tier compliance

### Rate Limiting (FR-022, FR-023)

- [X] T056 Create IP-based rate limiter (30/min, 500/day) in chatbot/app/middleware/rate_limiter.py
- [X] T057 Create RateLimitEntry in-memory model per data-model.md in chatbot/app/models/rate_limit.py
- [X] T058 Integrate rate limiter middleware with FastAPI in chatbot/app/main.py
- [X] T059 Add Retry-After header to 429 responses in chatbot/app/middleware/rate_limiter.py

### Error Handling

- [X] T060 [P] Create centralized error handler for all exception types in chatbot/app/middleware/error_handler.py
- [X] T061 [P] Add graceful degradation when Qdrant is unavailable in chatbot/app/services/search_service.py
- [X] T062 [P] Add graceful degradation when Neon is unavailable in chatbot/app/services/metadata_service.py
- [X] T063 Add structured logging for all error scenarios in chatbot/app/middleware/error_handler.py

### Health & Monitoring

- [X] T064 Extend health check to include Qdrant, Neon, Cohere, Gemini status in chatbot/app/routers/health.py
- [X] T065 Add request/response logging middleware in chatbot/app/middleware/logging.py

**Checkpoint**: Hardening complete - system is production-ready

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements before deployment

- [X] T066 [P] Create README.md with setup instructions in chatbot/README.md
- [X] T067 [P] Create deployment checklist for Hugging Face Spaces in chatbot/DEPLOYMENT.md
- [X] T068 Performance optimization: add response caching for repeated queries in chatbot/app/services/cache_service.py
- [X] T069 Run manual validation against all acceptance scenarios from spec.md
- [X] T070 Deploy to Hugging Face Spaces and verify end-to-end flow

---

## Phase 10: Bug Fixes & Build Issues

**Purpose**: Resolve critical build and configuration issues

- [X] T071 Fix Docusaurus build error: remove invalid devServer option from docusaurus.config.ts

---

## Phase 11: v2 Enhancements (Streaming & API Updates)

**Purpose**: Implement v2 API features per updated plan.md (Cohere embeddings, Gemini 2.5 Flash, streaming)

### Streaming Support

- [X] T072 [P] Create SSE streaming generator utility in chatbot/app/services/streaming_service.py
- [X] T073 Implement streaming response wrapper for Gemini 2.5 Flash in chatbot/app/services/agent_service.py
- [X] T074 Implement POST /chat/stream endpoint with SSE in chatbot/app/routers/chat.py
- [X] T075 Add streaming response handling in ChatWidget frontend in src/components/ChatWidget/ChatWidget.jsx

### Explicit Selected-Text Endpoint

- [X] T076 Implement POST /selected-text-query endpoint per api-spec.yaml in chatbot/app/routers/chat.py
- [X] T077 Add SelectedTextRequest validation (context_selection required) in chatbot/app/models/chat_request.py

### Health Check Updates

- [X] T078 Update health endpoint to include Cohere service status in chatbot/app/routers/health.py
- [X] T079 Add Cohere API ping utility for health check in chatbot/app/services/embedding_service.py

### Frontend v2 Updates

- [X] T080 [P] Add mode indicator badge in ChatWidget in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
- [X] T081 [P] Implement progressive text rendering for streaming in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
- [X] T082 Add connection retry logic for SSE failures in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx

### Integration & Validation

- [X] T083 Update CORS configuration for streaming headers in chatbot/app/main.py
- [X] T084 Test streaming endpoint with curl and browser EventSource
- [X] T085 Validate /selected-text-query endpoint behavior per api-spec.yaml
- [X] T086 Update deployment documentation for v2 features in chatbot/DEPLOYMENT_CHECKLIST.md

**Checkpoint**: v2 features complete - streaming and explicit endpoints functional ✅

---

## Phase 12: Critical Guardrails & Hardening (IMPLEMENTED)

**Purpose**: Critical improvements for selection-mode guardrails, streaming fallback, and collection versioning

### Selection-Mode Guardrail (CRITICAL)

- [X] T087 Add hard system instruction for selection mode forbidding external knowledge in chatbot/app/services/agent_service.py
- [X] T088 Implement "This information is not present in the selected text" response guardrail in chatbot/app/services/agent_service.py
- [X] T089 Create separate SELECTION_MODE_SYSTEM_PROMPT constant in chatbot/app/services/agent_service.py

### Streaming Fallback Logic (CRITICAL)

- [X] T090 Implement automatic fallback to non-streaming when streaming fails in chatbot/app/services/agent_service.py
- [X] T091 Add timeout protection for streaming responses in chatbot/app/services/agent_service.py
- [X] T092 Create StreamingService class with fallback utilities in chatbot/app/services/streaming_service.py
- [X] T093 Add structured logging for fallback events in chatbot/app/services/streaming_service.py

### Qdrant Collection Versioning (Recommended)

- [X] T094 Add versioned collection naming (book_embeddings_v2) in chatbot/app/services/vector_store.py
- [X] T095 Implement collection aliasing for seamless version switching in chatbot/app/services/vector_store.py
- [X] T096 Add create_new_version() and switch_alias_to_version() methods in chatbot/app/services/vector_store.py
- [X] T097 Update vector dimensions to 1024 for Cohere embeddings in chatbot/app/services/vector_store.py

### Frontend UX Mode Indicator (Recommended)

- [X] T098 Add mode indicator badge showing "Answering from selected text only" or "Answering from book content" in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx
- [X] T099 Add CSS styles for mode-selection and mode-retrieval badges in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.css
- [X] T100 Add responsive styles for mode indicator on mobile in physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.css

**Checkpoint**: Phase 12 complete - Critical guardrails implemented

---

## Dependencies & Execution Order

### Phase Dependencies

```
Setup (Phase 1)
    │
    ▼
Foundational (Phase 2)
    │
    ▼
Ingestion (Phase 3/US5) ◄── MUST complete before US1 can be tested
    │
    ├──► User Story 1 (Phase 4) - Retrieval Mode [P1] 🎯 MVP
    │         │
    │         ▼
    ├──► User Story 2 (Phase 5) - Selection Mode [P1]
    │         │
    │         ▼
    ├──► User Story 3 (Phase 6) - Out-of-Scope [P2]
    │
    └──► User Story 4 (Phase 7) - Mobile [P2] (can start in parallel)
              │
              ▼
         Hardening (Phase 8)
              │
              ▼
         Polish (Phase 9)
              │
              ▼
         Bug Fixes (Phase 10)
              │
              ▼
         v2 Enhancements (Phase 11) - Streaming & New Endpoints
```

### User Story Dependencies

| Story | Dependencies | Can Start After | Independent Test |
|-------|--------------|-----------------|------------------|
| US5 (Ingestion) | Phase 2 | Foundational | Ingest test chapter, query stores |
| US1 (Retrieval) | Phase 2 + US5 | Content ingested | Ask "What is inverse kinematics?" |
| US2 (Selection) | Phase 2 | Foundational (no content needed) | Select text, ask question |
| US3 (Out-of-Scope) | US1 | US1 complete | Ask "Stock price of Tesla?" |
| US4 (Mobile) | Frontend setup | Phase 1 | Access on 320px viewport |

### Parallel Opportunities

**Phase 2 (Foundational)** - Can run in parallel:
- T008, T009 (store schemas)
- T010, T011, T012, T013 (Pydantic models)

**Phase 3 (Ingestion)** - Can run in parallel:
- T020, T021 (chunker, URL mapper)

**Phase 4 (US1)** - Can run in parallel after T027:
- T028, T029 (search, metadata services)

**Phase 7 (US4)** - Can run in parallel with US1/US2/US3:
- T049, T050, T051, T052 (frontend components)

**Phase 8 (Hardening)** - Can run in parallel:
- T060, T061, T062 (error handlers)

**Phase 11 (v2 Enhancements)** - Can run in parallel:
- T072, T080, T081 (streaming utilities and frontend)
- T076, T077 (selected-text endpoint and model)
- T078, T079 (health check updates)

---

## Parallel Example: User Story 1

```bash
# After T027 (embedding service) completes:

# These can run in parallel (different files):
Task T028: "Create Qdrant similarity search service in chatbot/app/services/search_service.py"
Task T029: "Create Neon metadata lookup service in chatbot/app/services/metadata_service.py"

# Then sequentially:
Task T030: "Create context assembly service" (depends on T028, T029)
Task T031: "Create Google GenerativeAI integration" (depends on T030)
Task T034: "Implement POST /chat endpoint" (depends on T031)
```

---

## Implementation Strategy

### MVP First (User Stories 5 + 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 5 (Ingestion) - enables testing
4. Complete Phase 4: User Story 1 (Retrieval Mode)
5. **STOP and VALIDATE**: Test retrieval mode independently
6. Deploy to HF Spaces as MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US5 (Ingestion) → Content in stores
3. Add US1 (Retrieval) → **MVP deployed!**
4. Add US2 (Selection) → Enhanced UX
5. Add US3 (Out-of-Scope) → Better guardrails
6. Add US4 (Mobile) → Full accessibility
7. Hardening + Polish → Production-ready

### Context7 Checkpoints

Before implementing each service, use context7 to fetch current documentation:

| Task | Context7 Library |
|------|------------------|
| T022, T027, T079 | `cohere` (embed-english-v3.0) |
| T007, T009, T028 | `qdrant-client` |
| T006, T008, T029 | `asyncpg` or `psycopg2` |
| T031, T073 | `google-genai` (Gemini 2.5 Flash, streaming) |
| T016, T034, T074, T076 | `fastapi` (SSE, StreamingResponse) |
| T049-T055, T075, T080-T082 | `docusaurus`, React (EventSource for SSE) |

---

## Task Summary

| Phase | Task Range | Count | Description |
|-------|------------|-------|-------------|
| 1: Setup | T001-T005 | 5 | Project initialization |
| 2: Foundational | T006-T018 | 13 | Core infrastructure |
| 3: US5 Ingestion | T019-T026 | 8 | Content ingestion |
| 4: US1 Retrieval | T027-T036 | 10 | Retrieval mode |
| 5: US2 Selection | T037-T042 | 6 | Selection mode |
| 6: US3 Out-of-Scope | T043-T048 | 6 | Out-of-scope handling |
| 7: US4 Mobile | T049-T055 | 7 | Frontend/mobile |
| 8: Hardening | T056-T065 | 10 | Rate limiting, errors |
| 9: Polish | T066-T070 | 5 | Documentation, deploy |
| 10: Bug Fixes | T071 | 1 | Build error resolution |
| 11: v2 Enhancements | T072-T086 | 15 | Streaming, new endpoints |
| 12: Critical Guardrails | T087-T100 | 14 | Selection guardrails, streaming fallback |
| **Total** | T001-T100 | **100** | |

### v1 Complete (T001-T071): 71 tasks ✅

### v2 Scope (T072-T100): 29 tasks ✅

- Streaming support: 4 tasks (T072-T075) ✅
- Selected-text endpoint: 2 tasks (T076-T077) ✅
- Health updates: 2 tasks (T078-T079) ✅
- Frontend v2: 3 tasks (T080-T082) ✅
- Integration: 4 tasks (T083-T086) ✅
- Critical guardrails: 14 tasks (T087-T100) ✅

### All Tasks Complete: 100/100 ✅

### MVP Scope (US5 + US1)

- Setup: 5 tasks
- Foundational: 13 tasks
- US5 Ingestion: 8 tasks
- US1 Retrieval: 10 tasks
- **MVP Total**: 36 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use context7 before writing any service implementation
- All file paths assume hackathon-I/ as the root directory