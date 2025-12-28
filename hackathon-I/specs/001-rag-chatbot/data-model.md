# Data Model: RAG Chatbot

**Feature**: 001-rag-chatbot
**Created**: 2025-12-17
**Updated**: 2025-12-23
**Status**: Complete (v2)

## Entity Relationship Overview

```
┌─────────────────┐     ┌──────────────────┐
│  BookChunk      │────>│  ChunkEmbedding  │
│  (Neon Postgres)│     │  (Qdrant Cloud)  │
└─────────────────┘     └──────────────────┘
        │                       │
        │ referenced by         │ searched by
        ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  ChatSession    │     │  QueryEmbedding  │
│  (Neon Postgres)│     │  (Runtime/Cohere)│
└─────────────────┘     └──────────────────┘
        │
        │ contains
        ▼
┌─────────────────┐
│  ChatMessage    │
│  (Neon Postgres)│
└─────────────────┘
```

---

## 1. BookChunk (Neon Postgres)

**Purpose**: Stores raw book content with metadata for retrieval and citation.

**Table Name**: `book_chunks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `chunk_id` | UUID | PRIMARY KEY | Unique identifier for the chunk |
| `chapter` | VARCHAR(255) | NOT NULL | Human-readable chapter name |
| `section` | VARCHAR(255) | NULLABLE | Section within chapter (H2/H3 header) |
| `content` | TEXT | NOT NULL | Raw text content of chunk |
| `url` | VARCHAR(512) | NOT NULL | Full URL to the book page |
| `token_count` | INTEGER | NOT NULL | Token count for context budgeting |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Ingestion timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last modification timestamp |

**SQL Schema**:

```sql
CREATE TABLE book_chunks (
    chunk_id UUID PRIMARY KEY,
    chapter VARCHAR(255) NOT NULL,
    section VARCHAR(255),
    content TEXT NOT NULL,
    url VARCHAR(512) NOT NULL,
    token_count INTEGER NOT NULL CHECK (token_count > 0 AND token_count <= 600),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunk_chapter ON book_chunks(chapter);
CREATE INDEX idx_chunk_url ON book_chunks(url);
```

**Validation Rules**:
- `content` must be non-empty
- `url` must be valid URL format
- `token_count` must be > 0 and ≤ 600 (chunk size limit)

---

## 2. ChunkEmbedding (Qdrant Cloud)

**Purpose**: Stores vector embeddings for semantic search.

**Collection Name**: `book_embeddings`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Same as `chunk_id` in BookChunk (cross-reference) |
| `vector` | FLOAT[1024] | **Cohere embed-english-v3.0 output** |
| `payload.chapter` | STRING | Denormalized for filtering |
| `payload.section` | STRING | Denormalized for filtering |
| `payload.url` | STRING | For quick access without Neon lookup |
| `payload.token_count` | INTEGER | For context budgeting during retrieval |

**Vector Configuration**:
- **Dimensions**: 1024 (Cohere embed-english-v3.0)
- **Distance Metric**: Cosine
- **On-disk**: True (for free tier memory constraints)
- **Index**: HNSW with m=16, ef_construct=100

**Qdrant Setup Code**:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

client.create_collection(
    collection_name="book_embeddings",
    vectors_config=VectorParams(
        size=1024,  # Cohere embed-english-v3.0
        distance=Distance.COSINE,
        on_disk=True,
    ),
    hnsw_config=HnswConfigDiff(
        m=16,
        ef_construct=100,
    ),
)
```

---

## 3. ChatSession (Neon Postgres)

**Purpose**: Tracks conversation sessions for context management.

**Table Name**: `chat_sessions`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | UUID | PRIMARY KEY | UUID generated client-side |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Session start time |
| `last_activity` | TIMESTAMP | DEFAULT NOW() | Last interaction time |
| `message_count` | INTEGER | DEFAULT 0 | Total messages in session |

**SQL Schema**:

```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0
);

CREATE INDEX idx_session_activity ON chat_sessions(last_activity);
```

**Lifecycle**:
- Created: On first message with new session_id
- Active: Updated on each interaction
- Expired: After 30 minutes of inactivity (TTL cleanup)

---

## 4. ChatMessage (Neon Postgres)

**Purpose**: Stores conversation history for follow-up questions.

**Table Name**: `chat_messages`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `session_id` | UUID | REFERENCES chat_sessions | Session this message belongs to |
| `role` | VARCHAR(20) | CHECK IN ('user', 'assistant') | Message author |
| `content` | TEXT | NOT NULL | Message text |
| `context_mode` | VARCHAR(20) | NULLABLE | 'selection' or 'retrieval' (user msgs only) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Message timestamp |

**SQL Schema**:

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    context_mode VARCHAR(20) CHECK (context_mode IN ('selection', 'retrieval', NULL)),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_created ON chat_messages(created_at);
```

**Validation Rules**:
- `content` must be non-empty
- History limited to last 10 entries (5 Q&A pairs) per session

---

## 5. QueryContext (Runtime Object)

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
| `chapter` | STRING | For citation |
| `section` | STRING | For citation |
| `url` | STRING | For citation link |
| `similarity_score` | FLOAT | 0-1, only for retrieval mode |

**Pydantic Model**:

```python
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from enum import Enum

class ContextMode(str, Enum):
    SELECTION = "selection"
    RETRIEVAL = "retrieval"

class RetrievedChunk(BaseModel):
    chunk_id: UUID
    content: str
    chapter: str
    section: Optional[str]
    url: str
    similarity_score: Optional[float] = None  # Only for retrieval

class QueryContext(BaseModel):
    mode: ContextMode
    chunks: List[RetrievedChunk]
    total_tokens: int
    query: str
    session_id: str

    def validate_tokens(self) -> bool:
        return self.total_tokens <= 4000
```

**Validation Rules**:
- If `mode == 'selection'`, `chunks` contains exactly 1 item with user-selected text
- If `mode == 'retrieval'`, `chunks` contains 1-5 items from vector search
- `total_tokens` must not exceed 4000 (context budget)

---

## 6. Session Cleanup Function (Neon)

**Purpose**: Automatically clean up expired sessions.

```sql
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS void AS $$
BEGIN
    -- Delete messages first (foreign key constraint)
    DELETE FROM chat_messages
    WHERE session_id IN (
        SELECT session_id FROM chat_sessions
        WHERE last_activity < NOW() - INTERVAL '30 minutes'
    );

    -- Then delete sessions
    DELETE FROM chat_sessions
    WHERE last_activity < NOW() - INTERVAL '30 minutes';
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron or call periodically from application
-- SELECT cleanup_old_sessions();
```

---

## Cross-Reference Integrity

| Source | Target | Relationship | Enforcement |
|--------|--------|--------------|-------------|
| ChunkEmbedding.id | BookChunk.chunk_id | 1:1 | Application-level (ingestion) |
| ChatMessage.session_id | ChatSession.session_id | N:1 | Database FK with CASCADE |
| QueryContext.chunk_id | BookChunk.chunk_id | N:1 | Application-level (query time) |

**Note**: No foreign keys between Qdrant and Neon. Integrity maintained by:
1. Atomic ingestion (write both or neither)
2. UUID generation at ingestion time
3. Query-time validation (handle missing gracefully)

---

## Storage Estimates

| Entity | Count (Est.) | Size (Est.) | Storage |
|--------|--------------|-------------|---------|
| BookChunk | ~500 chunks | ~2 MB | Neon (512MB limit) |
| ChunkEmbedding | ~500 vectors | ~4 MB (1024 dims x 4 bytes x 500) | Qdrant (1GB limit) |
| ChatSession | ~100 concurrent | ~50 KB | Neon |
| ChatMessage | ~1000 messages | ~500 KB | Neon |

**Free Tier Compatibility**: ✅ Well within limits
- Neon: 512 MB free tier → ~3 MB used (< 1%)
- Qdrant: 1 GB free tier → ~4 MB used (< 1%)
- HF Spaces: 16 GB RAM (shared) → sufficient for in-memory operations

---

## API Request/Response Models

### ChatRequest

```python
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=36, max_length=36)
    context_selection: Optional[str] = Field(None, max_length=10000)
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    response: str
    mode: ContextMode
    sources: List[str] = []  # URLs for retrieval mode
    session_id: str
```

### HealthResponse

```python
class HealthResponse(BaseModel):
    status: str  # "healthy" or "degraded"
    version: str
    services: Dict[str, str]  # service -> status
```

---

## State Transitions

### BookChunk Lifecycle

```
[HTML Build] → PARSED → CHUNKED → EMBEDDED → STORED → ACTIVE
                                                        ↓
                                              (on re-ingest)
                                                        ↓
                                                   REPLACED
```

### ChatSession Lifecycle

```
[New Request] → CREATED → ACTIVE ←→ (each request updates last_activity)
                            ↓
                     (30min idle)
                            ↓
                        EXPIRED → REMOVED (cleanup function)
```

### QueryContext Lifecycle

```
[Request] → ASSEMBLED → VALIDATED → USED → DISCARDED
            (per-request, not persisted)
```

---

## Migration Notes

### From v1 (Gemini embeddings) to v2 (Cohere embeddings)

**Breaking Changes**:
1. Vector dimensions changed: 768 → 1024
2. Embedding model: Gemini embedding-001 → Cohere embed-english-v3.0
3. Collection must be recreated with new dimensions

**Migration Steps**:
1. Export chunk content from Neon (text + metadata)
2. Delete old Qdrant collection
3. Create new collection with 1024 dimensions
4. Re-embed all chunks using Cohere
5. Re-upload to Qdrant
6. Verify with test queries

**No Neon Changes Required**: Schema unchanged, only embedding source changes.
