---
id: 003
title: RAG Chatbot Implementation Plan
stage: plan
date: 2025-12-17
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: system
command: /sp.plan
labels: ["rag", "chatbot", "architecture", "planning", "implementation"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
  - specs/001-rag-chatbot/research.md
  - specs/001-rag-chatbot/data-model.md
  - specs/001-rag-chatbot/contracts/api-spec.yaml
tests:
  - none (planning phase)
---

## Prompt

You are acting as a senior AI systems architect and spec-driven engineer.

Goal:
Plan the implementation of an Integrated RAG Chatbot embedded inside an AI-native book, strictly following the spec.

Deliverables Required from This Plan:

1. Architecture Sketch (Textual) - High-level system architecture with clear separation of Frontend, Backend, Vector store, Metadata store, Embedding pipeline
2. Section Structure - Ingestion Pipeline, Embedding Strategy, Query Routing Logic, Selected Text Handling, Agent Prompt Design, Citation & Grounding Enforcement, Error & Out-of-Scope Handling, Frontend Integration
3. Research Approach (Concurrent) - What needs research, safe vs risky assumptions
4. Decisions Needing Documentation - Chunking strategy, embedding model choice, grounding enforcement location, out-of-scope detection
5. Testing Strategy (Acceptance-Criteria Driven) - Map tests to User Stories & FRs

## Response snapshot

Created comprehensive implementation plan with 4 artifacts:

**1. research.md** - Resolved 10 technical unknowns:
- Embedding: Gemini embedding-001 (768 dims, free tier)
- Chunking: Header-based with 2000 token fallback
- Out-of-scope: Combined similarity threshold (0.65) + LLM guardrail
- Rate limiting: IP-based sliding window (30/min, 500/day)
- Session: In-memory with 30min TTL

**2. data-model.md** - 5 entities defined:
- BookChunk (Neon Postgres): chunk_id, content, chapter_title, source_url
- ChunkEmbedding (Qdrant): id, vector[768], payload
- QueryContext (Runtime): mode, chunks, total_tokens
- ChatSession (In-Memory): session_id, messages, TTL
- RateLimitEntry (In-Memory): ip, counters

**3. contracts/api-spec.yaml** - OpenAPI 3.0 spec:
- POST /chat: Main query endpoint with selection/retrieval modes
- GET /health: Dependency health check
- Error responses: 400, 429, 500, 503

**4. plan.md** - Full implementation plan:
- System architecture diagram (ASCII)
- Constitution check: All principles PASS
- Request flows A (retrieval) and B (selection) with latency budgets
- 8 implementation sections mapped to FRs
- Testing strategy mapped to User Stories
- Risk register with mitigations
- 5-phase implementation order

## Outcome

- ✅ Impact: Complete architectural blueprint for RAG chatbot implementation
- 🧪 Tests: Testing strategy defined, mapped to all User Stories and FRs
- 📁 Files: 4 artifacts created (plan.md, research.md, data-model.md, api-spec.yaml)
- 🔁 Next prompts: /sp.tasks to generate task breakdown, /sp.adr for architectural decisions
- 🧠 Reflection: User input provided clear deliverable structure which guided comprehensive plan output

## Evaluation notes (flywheel)

- Failure modes observed: None - clear requirements from user
- Graders run and results (PASS/FAIL): Constitution check - PASS (all 5 principles)
- Prompt variant (if applicable): Detailed planning prompt with explicit deliverables
- Next experiment (smallest change to try): N/A - proceed to task generation
