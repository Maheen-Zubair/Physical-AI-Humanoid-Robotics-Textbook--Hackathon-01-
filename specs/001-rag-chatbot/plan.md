# Implementation Plan: Integrated RAG Chatbot

**Feature Branch**: `001-rag-chatbot`
**Created**: 2025-12-17
**Updated**: 2025-12-17
**Status**: Planning Complete
**Spec**: [spec.md](./spec.md)

---

## Context7 Integration Strategy

> **📚 Context7** is the MCP tool for fetching up-to-date documentation. It MUST be used throughout implementation for accurate, current API references.

### When to Use Context7

| Phase | Context7 Usage | Libraries to Fetch |
|-------|----------------|-------------------|
| Task Generation | Verify API capabilities | FastAPI, Qdrant, OpenAI SDK |
| Ingestion Code | Markdown parsing, embedding APIs | `markdown-it`, `google-generativeai`, `qdrant-client` |
| Backend Code | FastAPI patterns, Qdrant queries | `fastapi`, `qdrant-client`, `psycopg2`/`asyncpg` |
| Agent Code | OpenAI Agents SDK patterns | `openai`, `agents-sdk` |
| Frontend Code | ChatKit integration, React patterns | `@openai/chatkit`, `docusaurus` |
| Testing | pytest patterns, async testing | `pytest`, `pytest-asyncio`, `httpx` |

### Context7 Checkpoints

Before writing code for any section, run:
```
context7 resolve-library-id → get-library-docs
```

**Required lookups**:
- [ ] `qdrant-client` - Python client patterns
- [ ] `google-generativeai` - Embedding API usage
- [ ] `fastapi` - Async endpoints, CORS, middleware
- [ ] `openai` - Agents SDK, chat completions
- [ ] `docusaurus` - Plugin/component integration

---

## System Overview

The RAG Chatbot is an embedded question-answering system for an AI-native book. It operates in two mutually exclusive modes:

1. **Selection Mode**: User highlights text → chatbot answers using ONLY that text
2. **Retrieval Mode**: User asks question → semantic search → grounded response

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (GitHub Pages)                          │
│  ┌─────────────────┐    ┌──────────────────────────────────────────┐    │
│  │  Docusaurus     │    │           OpenAI ChatKit                 │    │
│  │  Book Content   │───>│  • Text selection capture                │    │
│  │                 │    │  • Query submission                      │    │
│  └─────────────────┘    │  • Response rendering (markdown)         │    │
│                         └──────────────────────────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTPS (CORS)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Hugging Face Spaces :7860)                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Server                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │   │
│  │  │ Rate Limiter│  │Query Router │  │  OpenAI Agents SDK      │   │   │
│  │  │ (IP-based)  │  │(sel vs ret) │  │  • System prompt        │   │   │
│  │  └─────────────┘  └─────────────┘  │  • Context injection    │   │   │
│  │                                     │  • Citation enforcement │   │   │
│  │                                     └─────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                          │                    │                          │
│              ┌───────────┴─────────┐          │                          │
│              ▼                     ▼          ▼                          │
│  ┌─────────────────┐   ┌─────────────────┐  ┌─────────────────┐         │
│  │  Qdrant Cloud   │   │  Neon Postgres  │  │   Gemini API    │         │
│  │  (Vectors)      │   │  (Metadata)     │  │  (Embeddings)   │         │
│  └─────────────────┘   └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| VI. Chatbot Accuracy | ✅ PASS | Grounding enforced via system prompt + citation validation |
| VII. Chatbot Clarity | ✅ PASS | Response length guidelines in agent prompt |
| VIII. Reproducibility | ✅ PASS | Deterministic embeddings, traceable chunk_ids |
| IX. Rigor | ✅ PASS | Selection mode uses ONLY user text; retrieval uses ONLY indexed content |
| Free Tier Constraint | ✅ PASS | All services within free tier limits |

---

## Environment Configuration

### Required Environment Variables

```bash
# Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgres://user:pass@host/db?sslmode=require

# Gemini API (Embeddings)
GEMINI_API_KEY=your-gemini-api-key

# OpenAI API (Agent/LLM)
OPENAI_API_KEY=your-openai-api-key

# Application Config
BOOK_BASE_URL=https://username.github.io/repo-name/docs
CORS_ORIGINS=["https://username.github.io"]
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_DAY=500
```

### Environment Variable Validation

```python
# Startup check (add to main.py)
REQUIRED_ENV = [
    "QDRANT_URL", "QDRANT_API_KEY",
    "DATABASE_URL",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "BOOK_BASE_URL"
]

def validate_environment():
    missing = [var for var in REQUIRED_ENV if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {missing}")
```

---

## Request Flows

### Flow A: Retrieval Mode (No Selection)

```
1. User submits query (no selection)
2. Rate limiter checks IP quota
3. Query router identifies: context_selection = null
4. [context7: google-generativeai] Gemini API generates query embedding
5. [context7: qdrant-client] Qdrant similarity search (top 3-5 chunks)
6. [context7: asyncpg] Neon lookup: chunk_ids → full text + URLs
7. Context assembled with citation metadata
   ├─ CHECKPOINT: Validate chunks have required fields
   └─ CHECKPOINT: Total tokens ≤ 4000
8. [context7: openai] OpenAI Agent generates response with citations
9. Post-processor validates citation presence
   └─ CHECKPOINT: Response contains [Source: ...](url) format
10. Response returned to ChatKit
```

**Latency Budget** (target ≤3s):
- Rate limit check: 5ms
- Embedding generation: 300ms
- Vector search: 200ms
- Neon lookup: 100ms
- LLM generation: 2000ms
- Post-processing: 50ms
- **Total**: ~2.6s ✅

### Flow B: Selection Mode (User Selection)

```
1. User selects text + submits query
2. Rate limiter checks IP quota
3. Query router identifies: context_selection = "..."
4. Validate selection:
   ├─ CHECKPOINT: Non-empty after strip()
   ├─ CHECKPOINT: Token count ≤ 4000
   └─ If invalid: Notify user, switch to retrieval mode
5. Context assembled from selection only (NO vector search)
   └─ CHECKPOINT: Log confirms zero Qdrant calls
6. [context7: openai] OpenAI Agent generates response
7. Post-processor validates response
   └─ CHECKPOINT: No external citations (selection mode)
8. Response returned with selection_mode flag
```

**Latency Budget** (target ≤3s):
- Rate limit check: 5ms
- Validation: 5ms
- LLM generation: 2000ms
- Post-processing: 50ms
- **Total**: ~2.1s ✅

---

## Implementation Sections

### Section 1: Ingestion Pipeline

> **Context7**: Use `markdown-it` for parsing, `google-generativeai` for embeddings, `qdrant-client` and `asyncpg` for storage.

**Purpose**: Parse Docusaurus Markdown → populate Qdrant + Neon

#### Book Content Location

```
Repository Structure:
hackathon-I/
├── docs/                          # Docusaurus book content
│   ├── intro.md                   # Introduction
│   ├── chapter-1/
│   │   ├── index.md               # Chapter 1 main
│   │   ├── section-1-1.md         # Section 1.1
│   │   └── section-1-2.md         # Section 1.2
│   ├── chapter-2/
│   │   └── ...
│   └── ...
└── chatbot/
    └── ingestion/
        └── ingest.py              # Ingestion script
```

#### URL Mapping Strategy

```python
def file_path_to_url(file_path: str, base_url: str) -> str:
    """
    Map local file path to deployed Docusaurus URL.

    Examples:
    - docs/intro.md → https://site.io/docs/intro
    - docs/chapter-1/index.md → https://site.io/docs/chapter-1
    - docs/chapter-1/section-1-1.md → https://site.io/docs/chapter-1/section-1-1
    """
    # Remove .md extension
    path = file_path.replace('.md', '')
    # Handle index files
    if path.endswith('/index'):
        path = path[:-6]
    # Remove docs/ prefix if present
    if path.startswith('docs/'):
        path = path[5:]
    return f"{base_url}/{path}"
```

#### Chunking Strategy

```python
# Header-based chunking with token fallback
CHUNK_CONFIG = {
    "primary_split": "##",      # H2 headers
    "secondary_split": "###",   # H3 if section > max_tokens
    "max_tokens": 2000,         # Gemini embedding limit
    "min_tokens": 100,          # Avoid fragments
    "overlap_tokens": 50,       # Context continuity
}
```

**Components**:
1. **Markdown Parser**: Extract content, headers, frontmatter
2. **Chunker**: Split by H2/H3 headers with token limit fallback
3. **URL Generator**: Map file paths to deployed URLs
4. **Embedding Generator**: Batch embed via Gemini API
5. **Dual Writer**: Atomic write to Qdrant + Neon

**Ingestion Script Interface**:
```bash
# Full re-ingestion
python ingestion/ingest.py --source ./docs --clear

# Incremental (future enhancement)
python ingestion/ingest.py --source ./docs --incremental
```

**FR Coverage**: FR-015, FR-016, FR-017, FR-018

**Key Decisions**:
- Chunking: Header-based with 2000 token max (see research.md)
- ID strategy: UUID per chunk, shared across stores
- Idempotency: Clear + re-ingest (no partial updates for MVP)

---

### Section 2: Embedding Strategy

> **Context7**: Use `google-generativeai` docs for embedding API patterns.

**Purpose**: Convert text to vectors for semantic search

**Configuration**:
- Model: `models/embedding-001` (Gemini)
- Dimensions: 768
- Batch size: 100 chunks per API call
- Rate limit: 1500 RPM (free tier)

```python
# Context7: Verify current Gemini embedding API
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"  # or "retrieval_query" for queries
    )
    return result['embedding']
```

**FR Coverage**: FR-010, FR-017

**Error Handling**:
- Retry with exponential backoff (3 attempts)
- Log failed chunks for manual review
- Continue ingestion on partial failures

---

### Section 3: Query Routing Logic

> **Context7**: Use `fastapi` docs for request handling patterns.

**Purpose**: Direct queries to correct processing path

**Decision Tree**:
```python
def route_query(request: ChatRequest) -> ContextMode:
    if request.context_selection:
        if request.context_selection.strip():
            # CHECKPOINT: Validate token count
            token_count = count_tokens(request.context_selection)
            if token_count > 4000:
                return ContextMode.SELECTION_TRUNCATED
            return ContextMode.SELECTION
        else:
            # Empty/whitespace selection
            notify_user("Selection was empty, searching book...")
            return ContextMode.RETRIEVAL
    return ContextMode.RETRIEVAL
```

**FR Coverage**: FR-006, FR-007, FR-009

---

### Section 4: Selected Text Handling

> **Context7**: Use `openai` docs for chat completion with custom context.

**Purpose**: Implement exclusive selection mode

**Constraints** (from spec):
- MUST use ONLY selected text as context
- MUST NOT perform vector search
- MUST provide feedback if selection was ignored

**Implementation**:
```python
if mode == ContextMode.SELECTION:
    # CHECKPOINT: Log that NO vector search occurs
    logger.info(f"Selection mode: skipping Qdrant search for session {session_id}")

    context = QueryContext(
        mode="selection",
        chunks=[{
            "content": request.context_selection,
            "chapter_title": "User Selection",
            "source_url": None,  # No URL for user selection
        }],
        total_tokens=count_tokens(request.context_selection)
    )
    # Skip vector search entirely - NO Qdrant calls
```

**FR Coverage**: FR-006, FR-007, FR-008, FR-009

---

### Section 5: Agent Prompt Design

> **Context7**: Use `openai` Agents SDK docs for system prompt patterns.

**Purpose**: Configure OpenAI Agent for grounded responses

**System Prompt Structure**:
```
You are a helpful assistant for readers of the Physical AI & Humanoid Robotics textbook.

RULES:
1. Answer ONLY using the provided context
2. If context is insufficient, say "I couldn't find information about that in the book"
3. Include citations in format: [Source: {title}]({url})
4. Keep responses concise and educational
5. If asked about topics not in context, politely decline

CONTEXT:
{formatted_context}
```

**Context Formatting**:
```python
def format_context(chunks: list[dict]) -> str:
    """Format chunks for agent context injection."""
    formatted = []
    for chunk in chunks:
        if chunk.get("source_url"):
            formatted.append(
                f'<context source="{chunk["chapter_title"]}" '
                f'url="{chunk["source_url"]}">\n{chunk["content"]}\n</context>'
            )
        else:
            # Selection mode - no URL
            formatted.append(
                f'<context source="User Selection">\n{chunk["content"]}\n</context>'
            )
    return "\n\n".join(formatted)
```

**FR Coverage**: FR-002, FR-003, FR-013, FR-014

---

### Section 6: Citation & Grounding Enforcement

> **Context7**: Reference `openai` docs for response parsing patterns.

**Purpose**: Ensure all responses cite sources properly

**Layers**:
1. **Prompt Instruction**: System prompt mandates citations
2. **Context Format**: Include metadata with each chunk
3. **Post-Validation**: Regex check for citation format

**Citation Format**:
```markdown
[Source: Chapter 5: Kinematics](https://book.site/docs/kinematics)
```

**Post-Processing with Checkpoints**:
```python
import re

CITATION_PATTERN = r'\[Source: [^\]]+\]\([^)]+\)'

def validate_citations(response: str, context: QueryContext) -> tuple[str, bool]:
    """
    Validate and fix citations in response.
    Returns (processed_response, citation_valid)
    """
    has_citation = bool(re.search(CITATION_PATTERN, response))

    # CHECKPOINT: Log citation validation result
    logger.info(f"Citation check: found={has_citation}, mode={context.mode}")

    if context.mode == "retrieval" and not has_citation:
        # Append fallback citation
        if context.chunks and context.chunks[0].get("source_url"):
            response += (
                f"\n\n[Source: {context.chunks[0]['chapter_title']}]"
                f"({context.chunks[0]['source_url']})"
            )
            logger.warning("Added fallback citation - LLM did not include one")
            return response, False

    return response, True
```

**FR Coverage**: FR-003, SC-005

---

### Section 7: Error & Out-of-Scope Handling

> **Context7**: Use `fastapi` docs for exception handling patterns.

**Purpose**: Graceful degradation and user feedback

**Scenarios**:

| Scenario | Detection | Response |
|----------|-----------|----------|
| Out-of-scope question | Low similarity (<0.65) + LLM uncertainty | "I couldn't find information about that in the book. Try asking about [related topic]." |
| Qdrant down | Connection error | "Search is temporarily unavailable. Please try again shortly." |
| Neon down | Connection error | Response without URLs: "Source links temporarily unavailable" |
| Rate limited | Counter exceeded | "Please wait {n} seconds before asking another question." |
| Empty selection | Whitespace check | "Your selection was empty. Searching the book instead..." |
| Large selection | Token count > 4000 | "Your selection is too long. Please select a shorter passage." |
| Missing env vars | Startup validation | Service fails to start with clear error message |

**FR Coverage**: FR-012, FR-013, FR-014, FR-020, FR-021, FR-022, FR-023

---

### Section 8: Frontend Integration (ChatKit)

> **Context7**: Use `@openai/chatkit` and `docusaurus` docs for integration patterns.

**Purpose**: Embed ChatKit in Docusaurus with selection capture

**Components**:
1. **ChatKit Widget**: OpenAI ChatKit React component
2. **Selection Listener**: Capture `window.getSelection()` on submit
3. **Session Manager**: Generate/persist session_id in localStorage
4. **Response Renderer**: Render markdown with clickable links

**Integration Points**:
```jsx
// Context7: Verify ChatKit API for message submission
// On message submit
const selection = window.getSelection()?.toString() || null;

// CHECKPOINT: Log selection capture
console.log(`Selection captured: ${selection ? selection.length : 0} chars`);

const response = await fetch(BACKEND_URL + '/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: userMessage,
    session_id: getSessionId(),
    context_selection: selection
  })
});
```

**FR Coverage**: FR-001, FR-008, FR-019, FR-020

---

## Potential Errors & Edge Cases

### Category 1: Token & Size Limits

| Error | Cause | Detection | Handling |
|-------|-------|-----------|----------|
| Large selection | User selects > 4000 tokens | Pre-submission token count | Truncate or reject with message |
| Large response | LLM generates verbose answer | Post-generation check | Truncate to 2000 tokens |
| Chunk too large | Source content has no headers | Ingestion validation | Force split at sentence boundary |

### Category 2: Infrastructure & Cold Start

| Error | Cause | Detection | Handling |
|-------|-------|-----------|----------|
| HF Spaces cold start | Container sleeping after idle | First request latency > 10s | Health check endpoint, user-facing loading indicator |
| Qdrant rate limit | Free tier exceeded | HTTP 429 response | Backoff + user message |
| Neon connection limit | Too many concurrent | Connection pool exhausted | Queue requests, increase pool |
| Gemini rate limit | Embedding quota exceeded | HTTP 429 response | Backoff during ingestion, fail query gracefully |

### Category 3: Data Quality

| Error | Cause | Detection | Handling |
|-------|-------|-----------|----------|
| Missing citation | LLM ignores prompt rule | Post-processing regex | Append fallback citation |
| Malformed metadata | Ingestion bug | Neon lookup returns null | Return response without source link |
| Stale content | Book updated, not re-ingested | Manual verification | Re-run ingestion, add ingestion timestamp |
| Duplicate chunks | Re-ingestion without clear | chunk_id collision | Always clear before full ingest |

### Category 4: Configuration

| Error | Cause | Detection | Handling |
|-------|-------|-----------|----------|
| Missing env var | Deployment misconfiguration | Startup validation | Fail fast with clear error |
| Wrong CORS origin | URL mismatch | Browser console error | Log expected vs actual origin |
| Invalid API key | Expired or wrong key | First API call fails | Clear error message, don't expose key |
| Wrong base URL | Book URL changed | Citations point to 404 | Health check includes URL validation |

### Category 5: Free Tier Limitations

| Service | Limit | Monitoring | Mitigation |
|---------|-------|------------|------------|
| Qdrant Cloud | 1GB storage, 1M vectors | Dashboard metrics | Alert at 80%, plan cleanup |
| Neon Postgres | 512MB storage | `pg_database_size()` | Alert at 80%, archive old data |
| Gemini API | 1500 RPM embeddings | Rate counter in logs | Batch ingestion, query throttling |
| OpenAI API | Varies by plan | Usage dashboard | Rate limiting, response caching |
| HF Spaces | 16GB RAM, CPU only | Container metrics | Optimize memory, lazy loading |

---

## Testing Strategy

### Unit Tests (Per Component)

> **Context7**: Use `pytest` and `pytest-asyncio` docs for async testing patterns.

| Component | Test Cases | FR/SC Coverage |
|-----------|------------|----------------|
| Chunker | Header split, token limit, overlap | FR-016 |
| Query Router | Selection detection, whitespace handling | FR-006, FR-009 |
| Citation Validator | Format check, missing citation | FR-003, SC-005 |
| Rate Limiter | Minute limit, daily limit, reset | FR-022, FR-023 |
| URL Mapper | Path to URL conversion | FR-018 |
| Token Counter | Accurate counts, edge cases | FR-009 (selection validation) |

### Integration Tests

| Test | Description | FR/SC Coverage |
|------|-------------|----------------|
| E2E Retrieval | Query → embedding → search → response | FR-010, FR-011, FR-012 |
| E2E Selection | Query + selection → response (no search) | FR-006, FR-007, SC-001 |
| Degraded Mode | Neon down → response without URLs | Edge case |
| Cold Start | First request after idle | Performance |

### Acceptance Tests (From Spec)

| User Story | Test | Pass Criteria |
|------------|------|---------------|
| US-1 | Ask "What is inverse kinematics?" | Response within 3s, citation present |
| US-2 | Select text, ask "Explain this" | Response uses ONLY selected text, zero Qdrant calls in logs |
| US-3 | Ask "Stock price of Tesla?" | Out-of-scope response |
| US-4 | Mobile viewport test | Usable at 320px width |
| US-5 | Ingest new chapter | Chatbot answers about new content |

### Performance Tests

| Metric | Target | Test Method |
|--------|--------|-------------|
| Response time | ≤3s | Load test with 10 concurrent users |
| Selected text rule | 100% | Log analysis: zero vector calls when selection present |
| Citation accuracy | 100% | Manual review of 50 sample responses |
| Cold start recovery | ≤15s | Measure first request after 30min idle |

---

## Architectural Decisions Requiring ADRs

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Chunking strategy | Fixed tokens, header-based, hybrid | Header + token hybrid | Preserves semantics while respecting limits |
| Out-of-scope detection | Threshold only, LLM only, combined | Combined | Higher accuracy with redundancy |
| Rate limit storage | Redis, in-memory, database | In-memory | Sufficient for single-instance HF Spaces |
| Session storage | Database, Redis, in-memory | In-memory | No persistence needed, simple implementation |
| Embedding model | OpenAI, Gemini, local | Gemini | Free tier, sufficient quality |

**📋 Architectural decision detected**: Embedding model selection (Gemini vs OpenAI)
Document reasoning and tradeoffs? Run `/sp.adr embedding-model-selection`

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 3s latency target missed | Medium | High | Profile bottlenecks, optimize LLM calls, consider caching |
| Gemini embedding quality | Low | Medium | Test retrieval accuracy, tune similarity threshold |
| Free tier limits exceeded | Low | High | Implement strict rate limiting, monitor usage dashboards |
| HF Spaces cold start | Medium | Medium | Health checks, user loading indicator, keep-warm cron |
| Large selection overflow | Medium | Low | Client-side token counter, server-side truncation |
| Missing citations | Medium | Medium | Post-processing fallback, prompt iteration |
| Env var misconfiguration | Low | High | Startup validation, deployment checklist |

---

## Implementation Order

1. **Phase 1: Ingestion Pipeline** (P3 prerequisite)
   - [ ] Markdown parser with frontmatter extraction
   - [ ] Header-based chunker with token fallback
   - [ ] URL mapper (file path → deployed URL)
   - [ ] Gemini embedding generator (with context7 lookup)
   - [ ] Dual-store writer (Qdrant + Neon atomic)

2. **Phase 2: Backend Core** (P1 features)
   - [ ] FastAPI scaffold with CORS (context7: fastapi)
   - [ ] Environment validation on startup
   - [ ] Query routing (selection vs retrieval)
   - [ ] Vector search integration (context7: qdrant-client)
   - [ ] Agent integration (context7: openai)

3. **Phase 3: Grounding & Safety** (P1/P2 features)
   - [ ] Citation enforcement (post-processing)
   - [ ] Out-of-scope detection (threshold + LLM)
   - [ ] Error handling for all edge cases
   - [ ] Large selection handling

4. **Phase 4: Frontend Integration** (P1/P2 features)
   - [ ] ChatKit embedding (context7: @openai/chatkit)
   - [ ] Selection capture on submit
   - [ ] Session management (localStorage)
   - [ ] Mobile responsiveness

5. **Phase 5: Hardening** (SC requirements)
   - [ ] Rate limiting (IP-based)
   - [ ] Performance optimization
   - [ ] Logging & monitoring
   - [ ] Health check endpoint

---

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research Document | `specs/001-rag-chatbot/research.md` | ✅ Complete |
| Data Model | `specs/001-rag-chatbot/data-model.md` | ✅ Complete |
| API Contract | `specs/001-rag-chatbot/contracts/api-spec.yaml` | ✅ Complete |
| Implementation Plan | `specs/001-rag-chatbot/plan.md` | ✅ Complete |

---

## Next Steps

1. Run `/sp.tasks` to generate task breakdown
2. Consider `/sp.adr embedding-model-selection` for ADR documentation
3. Begin implementation with ingestion pipeline
4. Use context7 for each library before writing implementation code
5. Validate environment variables in deployment checklist
