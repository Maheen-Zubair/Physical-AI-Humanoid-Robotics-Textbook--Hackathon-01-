# Data Model: RAG Chatbot

**Feature**: 001-rag-chatbot
**Created**: 2025-12-17
**Status**: Complete

## Entity Relationship Overview

```
┌─────────────────┐     ┌──────────────────┐
│  BookChunk      │────>│  ChunkEmbedding  │
│  (Neon Postgres)│     │  (Qdrant Cloud)  │
└─────────────────┘     └──────────────────┘
        │
        │ referenced by
        ▼
┌─────────────────┐
│  QueryContext   │
│  (Runtime)      │
└─────────────────┘
        │
        │ used in
        ▼
┌─────────────────┐
│  ChatSession    │
│  (In-Memory)    │
└─────────────────┘
```

---

## 1. BookChunk (Neon Postgres)

**Purpose**: Stores raw book content with metadata for retrieval and citation.

**Table Name**: `book_chunks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `chunk_id` | UUID | PRIMARY KEY | Unique identifier for the chunk |
| `chapter_title` | VARCHAR(255) | NOT NULL | Human-readable chapter name |
| `section_title` | VARCHAR(255) | NULLABLE | Section within chapter (H2/H3 header) |
| `content` | TEXT | NOT NULL | Raw markdown/text content of chunk |
| `source_url` | VARCHAR(512) | NOT NULL | Full URL to the book page |
| `chunk_index` | INTEGER | NOT NULL | Order within the chapter |
| `token_count` | INTEGER | NOT NULL | Approximate token count for context budgeting |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Ingestion timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last modification timestamp |

**Indexes**:
- `idx_chunk_chapter` on `chapter_title` (for chapter-level queries)
- `idx_chunk_url` on `source_url` (for URL-based lookups)

**Validation Rules**:
- `content` must be non-empty
- `source_url` must be valid URL format
- `token_count` must be > 0 and ≤ 2000

---

## 2. ChunkEmbedding (Qdrant Cloud)

**Purpose**: Stores vector embeddings for semantic search.

**Collection Name**: `book_embeddings`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Same as `chunk_id` in BookChunk (cross-reference) |
| `vector` | FLOAT[768] | Gemini embedding-001 output |
| `payload.chapter_title` | STRING | Denormalized for filtering |
| `payload.section_title` | STRING | Denormalized for filtering |
| `payload.token_count` | INTEGER | For context budgeting during retrieval |

**Vector Configuration**:
- Dimensions: 768 (Gemini embedding-001)
- Distance Metric: Cosine
- On-disk: True (for free tier memory constraints)

**Indexes**:
- HNSW index on vector field (Qdrant default)
- Payload index on `chapter_title` (optional filtering)

---

## 3. QueryContext (Runtime Object)

**Purpose**: Represents context assembled for a single query.

| Field | Type | Description |
|-------|------|-------------|
| `mode` | ENUM('selection', 'retrieval') | How context was obtained |
| `chunks` | List[RetrievedChunk] | Retrieved or selected content |
| `total_tokens` | INTEGER | Sum of chunk token counts |
| `query` | STRING | Original user query |
| `session_id` | STRING | Session identifier |

**RetrievedChunk** (nested):
| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | UUID | Reference to BookChunk |
| `content` | TEXT | Raw text content |
| `chapter_title` | STRING | For citation |
| `section_title` | STRING | For citation |
| `source_url` | STRING | For citation link |
| `similarity_score` | FLOAT | 0-1, only for retrieval mode |

**Validation Rules**:
- If `mode == 'selection'`, `chunks` contains exactly 1 item with user-selected text
- If `mode == 'retrieval'`, `chunks` contains 1-5 items from vector search
- `total_tokens` must not exceed 4000 (context budget)

---

## 4. ChatSession (In-Memory)

**Purpose**: Maintains conversation state for follow-up questions.

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | STRING | UUID generated client-side |
| `messages` | List[ChatMessage] | Conversation history |
| `created_at` | TIMESTAMP | Session start time |
| `last_activity` | TIMESTAMP | Last interaction time |

**ChatMessage** (nested):
| Field | Type | Description |
|-------|------|-------------|
| `role` | ENUM('user', 'assistant') | Message author |
| `content` | TEXT | Message text |
| `timestamp` | TIMESTAMP | Message time |
| `context_mode` | ENUM('selection', 'retrieval', null) | How context was obtained (user messages only) |

**Lifecycle**:
- Created: On first message with new session_id
- Active: Updated on each interaction
- Expired: After 30 minutes of inactivity (TTL cleanup)

**Validation Rules**:
- `messages` limited to last 10 entries (5 Q&A pairs)
- Total token count of history ≤ 2000 tokens

---

## 5. RateLimitEntry (In-Memory)

**Purpose**: Tracks request counts for rate limiting.

| Field | Type | Description |
|-------|------|-------------|
| `ip_address` | STRING | Client IP address |
| `minute_count` | INTEGER | Requests in current minute |
| `daily_count` | INTEGER | Requests today |
| `minute_reset` | TIMESTAMP | When minute counter resets |
| `daily_reset` | TIMESTAMP | When daily counter resets |

**Limits**:
- `minute_count` ≤ 30
- `daily_count` ≤ 500

---

## State Transitions

### BookChunk Lifecycle
```
[Source MD] → INGESTED → ACTIVE → (on re-ingest) → REPLACED
```

### ChatSession Lifecycle
```
[New Request] → CREATED → ACTIVE → (30min idle) → EXPIRED → REMOVED
```

### QueryContext Lifecycle
```
[Request] → ASSEMBLED → USED → DISCARDED (per-request, not stored)
```

---

## Cross-Reference Integrity

| Source | Target | Relationship | Enforcement |
|--------|--------|--------------|-------------|
| ChunkEmbedding.id | BookChunk.chunk_id | 1:1 | Application-level (ingestion) |
| QueryContext.chunk_id | BookChunk.chunk_id | N:1 | Application-level (query time) |
| ChatMessage.context_mode | QueryContext.mode | Reference | Application-level |

**Note**: No foreign keys between Qdrant and Neon. Integrity maintained by:
1. Atomic ingestion (write both or neither)
2. UUID generation at ingestion time
3. Query-time validation (handle missing gracefully)

---

## Storage Estimates

| Entity | Count (Est.) | Size (Est.) |
|--------|--------------|-------------|
| BookChunk | ~500 chunks | ~2 MB (Neon) |
| ChunkEmbedding | ~500 vectors | ~3 MB (Qdrant) |
| ChatSession | ~100 concurrent | ~1 MB (memory) |
| RateLimitEntry | ~1000 IPs | ~100 KB (memory) |

**Free Tier Compatibility**: ✅ Well within limits
- Neon: 512 MB free tier
- Qdrant: 1 GB free tier
- HF Spaces: 16 GB RAM (shared)
