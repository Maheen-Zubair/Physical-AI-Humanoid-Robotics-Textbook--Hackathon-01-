# Implementation Plan: Integrated RAG Chatbot

**Feature Branch**: `001-rag-chatbot`
**Created**: 2025-12-17
**Updated**: 2025-12-23
**Status**: Planning Complete (v2 - Deployment Ready)
**Spec**: [spec.md](./spec.md)

---

## Context7 Integration Strategy

> **Context7** is the MCP tool for fetching up-to-date documentation. It MUST be used throughout implementation for accurate, current API references.

### When to Use Context7

| Phase | Context7 Usage | Libraries to Fetch |
|-------|----------------|-------------------|
| Task Generation | Verify API capabilities | FastAPI, Qdrant, Cohere SDK |
| Ingestion Code | Build output parsing, embedding APIs | `beautifulsoup4`, `cohere`, `qdrant-client` |
| Backend Code | FastAPI patterns, Qdrant queries | `fastapi`, `qdrant-client`, `asyncpg` |
| Agent Code | OpenAI Agents SDK patterns | `openai`, `agents-sdk` |
| Response Gen | Gemini API for generation | `google-genai` |
| Frontend Code | ChatKit integration, React patterns | `@openai/chatkit`, `docusaurus` |
| Deployment | HuggingFace Spaces | `huggingface_hub`, `gradio` |
| Testing | pytest patterns, async testing | `pytest`, `pytest-asyncio`, `httpx` |

### Context7 Checkpoints

Before writing code for any section, run:
```
context7 resolve-library-id → get-library-docs
```

**Required lookups**:
- [x] `cohere` - Embed API v2 with embed-english-v3.0
- [x] `qdrant-client` - Python client patterns, upsert, search
- [x] `fastapi` - Async endpoints, CORS, middleware, streaming
- [x] `google-genai` - Gemini 2.5 Flash for generation
- [x] `huggingface_hub` - Spaces deployment
- [ ] `openai` - Agents SDK, chat completions
- [ ] `docusaurus` - Plugin/component integration

---

## System Overview

The RAG Chatbot is an embedded question-answering system for an AI-native book. It operates in two mutually exclusive modes:

1. **Selection Mode**: User highlights text → chatbot answers using ONLY that text
2. **Retrieval Mode**: User asks question → semantic search → grounded response

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (GitHub Pages)                                 │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐    │
│  │  Docusaurus     │    │           OpenAI ChatKit                     │    │
│  │  Book Content   │───>│  • Text selection capture                    │    │
│  │  (build folder) │    │  • Query submission                          │    │
│  └─────────────────┘    │  • Streaming response rendering              │    │
│                         └──────────────────────────────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS (CORS)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               BACKEND (Hugging Face Spaces - Docker :7860)                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Server                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────┐  │   │
│  │  │ Rate Limiter│  │Query Router │  │  OpenAI Agents SDK           │  │   │
│  │  │ (IP-based)  │  │(sel vs ret) │  │  • System prompt             │  │   │
│  │  └─────────────┘  └─────────────┘  │  • Context injection         │  │   │
│  │                                     │  • Citation enforcement      │  │   │
│  │  ENDPOINTS:                         └──────────────────────────────┘  │   │
│  │  • POST /chat                                                         │   │
│  │  • POST /selected-text-query                                          │   │
│  │  • GET /health                                                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                          │                    │                    │         │
│              ┌───────────┴─────────┐          │                    │         │
│              ▼                     ▼          ▼                    ▼         │
│  ┌─────────────────┐   ┌─────────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Qdrant Cloud   │   │  Neon Postgres  │  │ Cohere API  │  │ Gemini API │ │
│  │  (Vectors)      │   │  (Metadata +    │  │ (Embeddings)│  │ (Gen 2.5   │ │
│  │  HNSW Index     │   │   Sessions)     │  │ v3.0        │  │  Flash)    │ │
│  └─────────────────┘   └─────────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
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

## Technology Stack (Updated)

| Component | Technology | Version/Model | Notes |
|-----------|------------|---------------|-------|
| **Embeddings** | Cohere | `embed-english-v3.0` | 1024 dimensions, free tier |
| **Vector Store** | Qdrant Cloud | Free Tier | HNSW index, 1GB storage |
| **Response Gen** | Google Gemini | `gemini-2.5-flash` | Fast, cost-effective |
| **Backend** | FastAPI | 0.115+ | Async, streaming support |
| **Metadata Store** | Neon Postgres | Serverless | Chat history + chunk metadata |
| **RAG Orchestration** | OpenAI Agents SDK | Latest | Tool routing |
| **Frontend** | ChatKit + Docusaurus | - | Embedded widget |
| **Deployment** | Hugging Face Spaces | Docker SDK | Port 7860 |

---

## Environment Configuration

### Required Environment Variables

```bash
# Cohere API (Embeddings)
COHERE_API_KEY=your-cohere-api-key

# Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgres://user:pass@host/db?sslmode=require

# Gemini API (Response Generation)
GEMINI_API_KEY=your-gemini-api-key

# OpenAI API (Agent Orchestration)
OPENAI_API_KEY=your-openai-api-key

# Application Config
BOOK_BASE_URL=https://username.github.io/repo-name/docs
CORS_ORIGINS=["https://username.github.io"]
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_DAY=500
```

### Environment Variable Validation

```python
# config.py - Startup validation
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Required
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    database_url: str
    gemini_api_key: str
    openai_api_key: str
    book_base_url: str

    # Optional with defaults
    cors_origins: list[str] = ["https://username.github.io"]
    rate_limit_per_minute: int = 30
    rate_limit_per_day: int = 500

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Request Flows

### Flow A: Retrieval Mode (No Selection)

```
1. User submits query (no selection)
2. Rate limiter checks IP quota
3. Query router identifies: context_selection = null
4. [Context7: cohere] Cohere API generates query embedding (embed-english-v3.0)
5. [Context7: qdrant-client] Qdrant similarity search (top_k=5, threshold ≥0.7)
6. [Context7: asyncpg] Neon lookup: chunk_ids → full text + URLs
7. Context assembled with citation metadata
   ├─ CHECKPOINT: Validate chunks have required fields
   └─ CHECKPOINT: Total tokens ≤ 4000
8. [Context7: google-genai] Gemini 2.5 Flash generates response with citations
9. Post-processor validates citation presence
   └─ CHECKPOINT: Response contains [Source: ...](url) format
10. Streaming response returned to ChatKit
```

**Latency Budget** (target ≤3s):
- Rate limit check: 5ms
- Cohere embedding generation: 200ms
- Qdrant vector search: 150ms
- Neon lookup: 100ms
- Gemini generation (streaming): 1500ms
- Post-processing: 50ms
- **Total**: ~2.0s ✅

### Flow B: Selection Mode (User Selection)

```
1. User selects text + submits query
2. Rate limiter checks IP quota
3. Query router identifies: context_selection = "..."
4. Validate selection:
   ├─ CHECKPOINT: Non-empty after strip()
   ├─ CHECKPOINT: Token count ≤ 4000
   └─ If invalid: Notify user, switch to retrieval mode
5. Context assembled from selection only (NO vector search, NO embedding)
   └─ CHECKPOINT: Log confirms zero Qdrant/Cohere calls
6. [Context7: google-genai] Gemini 2.5 Flash generates response
7. Post-processor validates response
   └─ CHECKPOINT: No external citations (selection mode)
8. Streaming response returned with selection_mode flag
```

**Latency Budget** (target ≤3s):
- Rate limit check: 5ms
- Validation: 5ms
- Gemini generation (streaming): 1500ms
- Post-processing: 50ms
- **Total**: ~1.6s ✅

---

## Implementation Sections

### Section 1: Content Ingestion Pipeline

> **Context7**: Use `beautifulsoup4` for HTML parsing, `cohere` for embeddings, `qdrant-client` and `asyncpg` for storage.

**Purpose**: Parse Docusaurus build output → populate Qdrant + Neon

#### Source Content Location

```
Repository Structure:
hackathon-I/
├── physical-ai-robotics-book/
│   └── build/                      # Docusaurus build output
│       ├── index.html
│       ├── docs/
│       │   ├── intro/index.html
│       │   ├── chapter-1/
│       │   │   ├── index.html
│       │   │   └── section-1/index.html
│       │   └── ...
│       └── assets/
└── chatbot/
    └── ingestion/
        ├── ingest.py               # Main ingestion script
        ├── chunker.py              # Text chunking logic
        ├── embedder.py             # Cohere embedding client
        └── storage.py              # Qdrant + Neon writers
```

#### Chunking Strategy

```python
# chunker.py - ~500 tokens per chunk with 50-token overlap
CHUNK_CONFIG = {
    "target_tokens": 500,           # Target chunk size
    "overlap_tokens": 50,           # Context continuity
    "max_tokens": 600,              # Hard limit
    "min_tokens": 100,              # Avoid fragments
    "split_on": ["## ", "### ", "\n\n", ". "],  # Priority order
}

def chunk_content(text: str, metadata: dict) -> list[dict]:
    """
    Split content into ~500 token chunks with 50-token overlap.

    Returns:
        List of chunk dicts with: content, chunk_id, metadata
    """
    chunks = []
    # Implementation: recursive split on headers, then paragraphs
    # Include metadata: chapter, section, page/URL, chunk_id
    return chunks
```

#### Cohere Embedding Integration

```python
# embedder.py - Using Cohere embed-english-v3.0
# Context7: /cohere-ai/cohere-python - embed API

import cohere
from typing import List

class CohereEmbedder:
    def __init__(self, api_key: str):
        self.client = cohere.Client(token=api_key)
        self.model = "embed-english-v3.0"
        self.dimensions = 1024

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents for storage (max 96 per call)."""
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document",
            truncate="END"
        )
        return response.embeddings

    def embed_query(self, query: str) -> List[float]:
        """Embed a query for search."""
        response = self.client.embed(
            texts=[query],
            model=self.model,
            input_type="search_query",
            truncate="END"
        )
        return response.embeddings[0]
```

#### Qdrant Collection Setup

```python
# storage.py - Qdrant setup with HNSW
# Context7: /qdrant/qdrant-client - collection, upsert

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    HnswConfigDiff, OptimizersConfigDiff
)

def setup_qdrant_collection(client: QdrantClient, collection_name: str):
    """Create collection with HNSW index for Cohere 1024-dim vectors."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,  # Cohere embed-english-v3.0
                distance=Distance.COSINE,
                on_disk=True,  # Free tier memory optimization
            ),
            hnsw_config=HnswConfigDiff(
                m=16,
                ef_construct=100,
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=0,  # Index immediately
            ),
        )

def upsert_embeddings(
    client: QdrantClient,
    collection_name: str,
    chunks: list[dict],
    embeddings: list[list[float]]
):
    """Upsert chunk embeddings with metadata payload."""
    points = [
        PointStruct(
            id=chunk["chunk_id"],
            vector=embedding,
            payload={
                "chapter": chunk["chapter"],
                "section": chunk["section"],
                "url": chunk["url"],
                "token_count": chunk["token_count"],
            }
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )
```

#### Ingestion Script Interface

```bash
# Full ingestion from Docusaurus build
python ingestion/ingest.py \
    --source ./physical-ai-robotics-book/build \
    --clear \
    --batch-size 50

# Verify ingestion
python ingestion/verify.py --collection book_embeddings
```

**FR Coverage**: FR-015, FR-016, FR-017, FR-018

---

### Section 2: Embedding Pipeline Details

> **Context7**: Use `cohere` docs for embed-english-v3.0 patterns.

**Configuration**:
- Model: `embed-english-v3.0` (Cohere)
- Dimensions: 1024
- Batch size: 96 texts per API call (Cohere limit)
- Input types: `search_document` for indexing, `search_query` for queries
- Rate limit: Free tier allows ~100 calls/minute

**Embedding Code Pattern**:

```python
# Context7: /cohere-ai/cohere-python - embed API v2
from cohere import Client

client = Client(token=os.environ["COHERE_API_KEY"])

# For documents (ingestion)
response = client.embed(
    texts=["chunk 1 text", "chunk 2 text"],
    model="embed-english-v3.0",
    input_type="search_document",
    embedding_types=["float"],
    truncate="END"
)
doc_embeddings = response.embeddings

# For queries (runtime)
response = client.embed(
    texts=["user question here"],
    model="embed-english-v3.0",
    input_type="search_query",
    embedding_types=["float"],
    truncate="END"
)
query_embedding = response.embeddings[0]
```

**Error Handling**:
- Retry with exponential backoff (3 attempts, 1s/2s/4s delays)
- Log failed chunks for manual review
- Continue ingestion on partial failures
- Fallback: Return graceful error if Cohere unavailable

**FR Coverage**: FR-010, FR-017

---

### Section 3: Retrieval & RAG Orchestration

> **Context7**: Use `qdrant-client` for search, threshold filtering.

**Similarity Search Configuration**:

```python
# retrieval.py - Vector search with score threshold
# Context7: /qdrant/qdrant-client - search

from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams

def search_similar_chunks(
    client: QdrantClient,
    collection_name: str,
    query_embedding: list[float],
    top_k: int = 5,
    score_threshold: float = 0.7
) -> list[dict]:
    """
    Search for similar chunks with score threshold.

    Returns chunks with similarity >= 0.7 only.
    """
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k,
        score_threshold=score_threshold,
        search_params=SearchParams(
            hnsw_ef=128,  # Higher = more accurate
            exact=False,
        ),
    )

    return [
        {
            "chunk_id": str(hit.id),
            "score": hit.score,
            "chapter": hit.payload["chapter"],
            "section": hit.payload["section"],
            "url": hit.payload["url"],
            "token_count": hit.payload["token_count"],
        }
        for hit in results
    ]
```

**Optional Reranking** (future enhancement):
```python
# Using Cohere rerank for improved precision
def rerank_results(query: str, chunks: list[dict], top_n: int = 3):
    response = client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[c["content"] for c in chunks],
        top_n=top_n
    )
    return [chunks[r.index] for r in response.results]
```

**FR Coverage**: FR-010, FR-011, FR-012

---

### Section 4: Query Routing Logic

> **Context7**: Use `fastapi` docs for request handling patterns.

**Purpose**: Direct queries to correct processing path

**Request Models**:

```python
# models.py - Pydantic models for API
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ContextMode(str, Enum):
    SELECTION = "selection"
    RETRIEVAL = "retrieval"
    SELECTION_INVALID = "selection_invalid"

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=36, max_length=36)
    context_selection: Optional[str] = Field(None, max_length=10000)

class ChatResponse(BaseModel):
    response: str
    mode: ContextMode
    sources: list[dict] = []
    session_id: str
```

**Routing Logic**:

```python
# router.py - Query routing
import tiktoken

def count_tokens(text: str) -> int:
    """Approximate token count."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def route_query(request: ChatRequest) -> tuple[ContextMode, str | None]:
    """
    Determine context mode based on request.

    Returns:
        (mode, feedback_message)
    """
    if request.context_selection:
        selection = request.context_selection.strip()

        if not selection:
            # Empty/whitespace selection
            return ContextMode.RETRIEVAL, "Selection was empty, searching book..."

        token_count = count_tokens(selection)
        if token_count > 4000:
            return ContextMode.SELECTION_INVALID, \
                f"Selection too long ({token_count} tokens). Max 4000. Please select shorter text."

        return ContextMode.SELECTION, None

    return ContextMode.RETRIEVAL, None
```

**FR Coverage**: FR-006, FR-007, FR-009

---

### Section 5: Response Generation with Gemini

> **Context7**: Use `google-genai` docs for Gemini 2.5 Flash.

**Purpose**: Generate grounded, citation-aware responses

**Gemini Client Setup**:

```python
# generator.py - Gemini 2.5 Flash for response generation
# Context7: /googleapis/python-genai - generate_content

from google import genai
from google.genai import types

class GeminiGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def generate_response(
        self,
        query: str,
        context: str,
        mode: str,
        system_instruction: str
    ) -> str:
        """Generate a grounded response using Gemini 2.5 Flash."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_instruction}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query}",
            config=types.GenerateContentConfig(
                temperature=0.3,  # Lower for factual responses
                max_output_tokens=1024,
                top_p=0.9,
            )
        )
        return response.text

    def generate_stream(
        self,
        query: str,
        context: str,
        mode: str,
        system_instruction: str
    ):
        """Stream response for real-time UI updates."""
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=f"{system_instruction}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query}",
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
        for chunk in response:
            yield chunk.text
```

**System Prompt Template**:

```python
RETRIEVAL_SYSTEM_PROMPT = """You are a helpful assistant for readers of the Physical AI & Humanoid Robotics textbook.

RULES:
1. Answer ONLY using the provided context - do not use external knowledge
2. If context is insufficient, say "I couldn't find information about that in the book"
3. ALWAYS include citations in format: [Source: {title}]({url})
4. Keep responses concise, educational, and well-structured
5. If asked about topics not in context, politely decline

CONTEXT FORMAT:
Each context block contains:
- source: Chapter/section title
- url: Link to the source page
- content: The actual text content

Always cite sources when using information from context blocks.
"""

SELECTION_SYSTEM_PROMPT = """You are a helpful assistant explaining user-selected text from a textbook.

RULES:
1. Focus ONLY on the selected text provided
2. Explain, clarify, or elaborate as requested
3. Do NOT cite external sources - you are explaining the user's selection
4. Keep explanations clear and educational
5. If the selection is unclear, ask for clarification
"""
```

**FR Coverage**: FR-002, FR-003, FR-005, FR-013, FR-014

---

### Section 6: Backend API Architecture

> **Context7**: Use `fastapi` for endpoints, CORS, streaming.

**FastAPI Application Structure**:

```python
# main.py - FastAPI application
# Context7: /fastapi/fastapi - CORS, streaming

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

app = FastAPI(
    title="RAG Chatbot API",
    version="2.0.0",
    docs_url="/docs",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "X-Session-ID"],
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for HF Spaces."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "qdrant": await check_qdrant(),
            "neon": await check_neon(),
            "cohere": await check_cohere(),
            "gemini": await check_gemini(),
        }
    }

@app.post("/chat")
@limiter.limit("30/minute;500/day")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint - handles both retrieval and selection modes.
    """
    mode, feedback = route_query(body)

    if mode == ContextMode.SELECTION:
        context = format_selection_context(body.context_selection)
        response = await generate_selection_response(body.query, context)
    else:
        # Retrieval mode
        embedding = await embed_query(body.query)
        chunks = await search_chunks(embedding)
        context = await enrich_chunks_from_neon(chunks)
        response = await generate_retrieval_response(body.query, context)

    return ChatResponse(
        response=response,
        mode=mode,
        sources=[c["url"] for c in context] if mode == ContextMode.RETRIEVAL else [],
        session_id=body.session_id,
    )

@app.post("/chat/stream")
@limiter.limit("30/minute;500/day")
async def chat_stream(request: Request, body: ChatRequest):
    """Streaming chat endpoint for real-time responses."""
    async def generate():
        mode, feedback = route_query(body)

        if mode == ContextMode.SELECTION:
            context = format_selection_context(body.context_selection)
            async for chunk in stream_selection_response(body.query, context):
                yield f"data: {chunk}\n\n"
        else:
            embedding = await embed_query(body.query)
            chunks = await search_chunks(embedding)
            context = await enrich_chunks_from_neon(chunks)
            async for chunk in stream_retrieval_response(body.query, context):
                yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/selected-text-query")
@limiter.limit("30/minute;500/day")
async def selected_text_query(request: Request, body: ChatRequest):
    """
    Explicit selected-text-only endpoint.
    MUST have context_selection, NEVER performs vector search.
    """
    if not body.context_selection or not body.context_selection.strip():
        raise HTTPException(
            status_code=400,
            detail="context_selection is required for this endpoint"
        )

    context = format_selection_context(body.context_selection)
    response = await generate_selection_response(body.query, context)

    return ChatResponse(
        response=response,
        mode=ContextMode.SELECTION,
        sources=[],
        session_id=body.session_id,
    )
```

**FR Coverage**: FR-001, FR-008, FR-019, FR-020, FR-021, FR-022, FR-023

---

### Section 7: Data Persistence (Neon PostgreSQL)

> **Context7**: Use `asyncpg` for async Postgres operations.

**Database Schema**:

```sql
-- schema.sql - Neon Serverless PostgreSQL

-- Book content chunks (metadata only, embeddings in Qdrant)
CREATE TABLE book_chunks (
    chunk_id UUID PRIMARY KEY,
    chapter VARCHAR(255) NOT NULL,
    section VARCHAR(255),
    content TEXT NOT NULL,
    url VARCHAR(512) NOT NULL,
    token_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunk_chapter ON book_chunks(chapter);
CREATE INDEX idx_chunk_url ON book_chunks(url);

-- Chat sessions and history
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(session_id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    context_mode VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);

-- Session cleanup (run periodically)
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM chat_messages
    WHERE session_id IN (
        SELECT session_id FROM chat_sessions
        WHERE last_activity < NOW() - INTERVAL '30 minutes'
    );
    DELETE FROM chat_sessions
    WHERE last_activity < NOW() - INTERVAL '30 minutes';
END;
$$ LANGUAGE plpgsql;
```

**Async Database Client**:

```python
# database.py - Async Postgres client
import asyncpg
from contextlib import asynccontextmanager

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url, min_size=2, max_size=10)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[dict]:
        """Fetch full chunk content from Neon by IDs."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT chunk_id, chapter, section, content, url, token_count
                FROM book_chunks
                WHERE chunk_id = ANY($1)
                """,
                chunk_ids
            )
            return [dict(row) for row in rows]

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        context_mode: str = None
    ):
        """Save a chat message to history."""
        async with self.pool.acquire() as conn:
            # Upsert session
            await conn.execute(
                """
                INSERT INTO chat_sessions (session_id, last_activity, message_count)
                VALUES ($1, NOW(), 1)
                ON CONFLICT (session_id)
                DO UPDATE SET last_activity = NOW(), message_count = chat_sessions.message_count + 1
                """,
                session_id
            )
            # Insert message
            await conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, context_mode)
                VALUES ($1, $2, $3, $4)
                """,
                session_id, role, content, context_mode
            )
```

**FR Coverage**: FR-004, FR-018

---

### Section 8: Frontend Integration (ChatKit)

> **Context7**: Use `@openai/chatkit` and `docusaurus` docs for integration.

**Purpose**: Embed ChatKit in Docusaurus with selection capture

**ChatWidget Component**:

```jsx
// src/components/ChatWidget/index.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import styles from './styles.module.css';

const BACKEND_URL = 'https://your-space.hf.space';

export default function ChatWidget() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(() => {
        // Persist session in localStorage
        const stored = localStorage.getItem('chatbot_session_id');
        if (stored) return stored;
        const newId = uuidv4();
        localStorage.setItem('chatbot_session_id', newId);
        return newId;
    });

    const getSelectedText = useCallback(() => {
        const selection = window.getSelection();
        if (selection && selection.toString().trim()) {
            return selection.toString().trim();
        }
        return null;
    }, []);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const selectedText = getSelectedText();
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch(`${BACKEND_URL}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: input,
                    session_id: sessionId,
                    context_selection: selectedText,
                }),
            });

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = { role: 'assistant', content: '' };
            setMessages(prev => [...prev, assistantMessage]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                        const text = line.slice(6);
                        assistantMessage.content += text;
                        setMessages(prev => {
                            const newMessages = [...prev];
                            newMessages[newMessages.length - 1] = { ...assistantMessage };
                            return newMessages;
                        });
                    }
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.chatWidget}>
            <div className={styles.header}>
                <span>Book Assistant</span>
                <span className={styles.hint}>
                    Tip: Select text to ask about specific content
                </span>
            </div>
            <div className={styles.messages}>
                {messages.map((msg, i) => (
                    <div key={i} className={styles[msg.role]}>
                        {msg.content}
                    </div>
                ))}
                {isLoading && <div className={styles.loading}>Thinking...</div>}
            </div>
            <div className={styles.inputArea}>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask about the book..."
                    disabled={isLoading}
                />
                <button onClick={sendMessage} disabled={isLoading}>
                    Send
                </button>
            </div>
        </div>
    );
}
```

**Docusaurus Integration**:

```javascript
// docusaurus.config.ts - Add client module
module.exports = {
  // ... existing config
  clientModules: [
    require.resolve('./src/clientModules.js'),
  ],
};

// src/clientModules.js
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

if (ExecutionEnvironment.canUseDOM) {
    // Inject ChatWidget into page
    import('./components/ChatWidget').then(({ default: ChatWidget }) => {
        // Mount logic
    });
}
```

**FR Coverage**: FR-001, FR-008, FR-019, FR-020

---

### Section 9: Hugging Face Spaces Deployment

> **Context7**: Use `huggingface_hub` for Spaces deployment.

**Dockerfile for HF Spaces**:

```dockerfile
# Dockerfile - HuggingFace Spaces Docker SDK
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# HuggingFace Spaces expects port 7860
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**requirements.txt**:

```
# Core
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Embeddings & Vector Search
cohere>=5.0.0
qdrant-client>=1.9.0

# LLM
google-genai>=1.0.0
openai>=1.0.0

# Database
asyncpg>=0.29.0

# Rate Limiting
slowapi>=0.1.9

# Utilities
tiktoken>=0.7.0
python-dotenv>=1.0.0
httpx>=0.27.0
```

**HuggingFace Space Configuration**:

```yaml
# README.md (HF Space metadata)
---
title: RAG Chatbot for Physical AI Book
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# RAG Chatbot API

Backend API for the Physical AI & Humanoid Robotics textbook chatbot.

## Endpoints

- `GET /health` - Health check
- `POST /chat` - Main chat endpoint
- `POST /chat/stream` - Streaming chat endpoint
- `POST /selected-text-query` - Selected text only mode
```

**Environment Variables in HF Spaces**:

Set via Settings > Repository secrets:
- `COHERE_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `BOOK_BASE_URL`
- `CORS_ORIGINS`

**Deployment Commands**:

```bash
# Using huggingface_hub CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Create space
huggingface-cli repo create rag-chatbot-api --type space --space_sdk docker

# Push code
cd chatbot
git init
git remote add space https://huggingface.co/spaces/USERNAME/rag-chatbot-api
git add .
git commit -m "Initial deployment"
git push space main
```

---

### Section 10: Configuration & Fallback Strategies

**API Limits and Fallbacks**:

| Service | Free Tier Limit | Fallback Strategy |
|---------|-----------------|-------------------|
| Cohere | 100 API calls/min | Queue requests, retry with backoff |
| Qdrant | 1GB storage, 1M vectors | Alert at 80%, archive old data |
| Neon | 512MB storage | Cleanup old sessions, compress |
| Gemini | Rate varies | Exponential backoff, cache responses |
| HF Spaces | 16GB RAM, 2 vCPU | Optimize memory, lazy loading |

**Fallback Implementation**:

```python
# fallback.py - Graceful degradation
import asyncio
from functools import wraps

def with_fallback(fallback_value, max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.error(f"All retries failed for {func.__name__}: {e}")
                        return fallback_value
        return wrapper
    return decorator

@with_fallback(fallback_value=[], max_retries=3)
async def embed_query(query: str):
    return await cohere_client.embed_query(query)

@with_fallback(fallback_value="I'm having trouble connecting. Please try again.", max_retries=2)
async def generate_response(query: str, context: str):
    return await gemini_client.generate(query, context)
```

---

### Section 11: Validation & Testing

**Test Categories**:

| Test Type | Description | Tools |
|-----------|-------------|-------|
| Unit Tests | Individual functions | pytest, pytest-asyncio |
| Integration Tests | API endpoints | httpx, pytest |
| E2E Tests | Full user flow | playwright |
| Load Tests | Concurrent users | locust |

**Test Examples**:

```python
# tests/test_retrieval.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_retrieval_mode():
    """Test retrieval mode returns sources."""
    async with AsyncClient(base_url="http://localhost:7860") as client:
        response = await client.post("/chat", json={
            "query": "What is inverse kinematics?",
            "session_id": "test-session-123",
            "context_selection": None
        })
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "retrieval"
        assert len(data["sources"]) > 0
        assert "[Source:" in data["response"]

@pytest.mark.asyncio
async def test_chat_selection_mode():
    """Test selection mode uses ONLY selected text."""
    async with AsyncClient(base_url="http://localhost:7860") as client:
        response = await client.post("/chat", json={
            "query": "Explain this in simpler terms",
            "session_id": "test-session-123",
            "context_selection": "Inverse kinematics is the mathematical process..."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "selection"
        assert data["sources"] == []  # No external sources

@pytest.mark.asyncio
async def test_qdrant_embeddings():
    """Verify embeddings exist in Qdrant."""
    from qdrant_client import QdrantClient
    client = QdrantClient(url=os.environ["QDRANT_URL"])

    info = client.get_collection("book_embeddings")
    assert info.points_count > 0
    assert info.config.params.vectors.size == 1024  # Cohere dimensions

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting enforcement."""
    async with AsyncClient(base_url="http://localhost:7860") as client:
        # Make 31 requests in quick succession
        responses = []
        for _ in range(31):
            r = await client.post("/chat", json={
                "query": "test",
                "session_id": "rate-test",
                "context_selection": None
            })
            responses.append(r.status_code)

        assert 429 in responses  # Rate limit hit
```

**FR/SC Coverage**:
- SC-001: 100% selection mode constraint
- SC-002: ≤3s response time
- SC-005: Citation format validation
- SC-007: Free tier compliance

---

### Section 12: Gap Analysis

**Identified Gaps**:

| Gap | Impact | Mitigation |
|-----|--------|------------|
| Cold start latency on HF Spaces | First request may be slow | Implement keep-warm cron, loading indicator |
| Cohere rate limits | May throttle heavy usage | Queue requests, implement backoff |
| No user auth | Can't personalize | Use session_id for short-term context |
| Streaming support in ChatKit | May need custom implementation | Fallback to non-streaming if needed |

**Blockers**: None identified - all dependencies available on free tiers.

**Assumptions**:
1. Docusaurus build output is available in `build/` folder
2. HTML structure follows standard Docusaurus patterns
3. Free tier limits are sufficient for expected traffic
4. Cohere embed-english-v3.0 quality is adequate for RAG

---

## Implementation Order

### Phase 1: Ingestion Pipeline (Day 1-2)
- [ ] Build folder HTML parser with BeautifulSoup
- [ ] Chunking with ~500 tokens, 50-token overlap
- [ ] Cohere embedding integration (embed-english-v3.0)
- [ ] Qdrant collection setup with HNSW
- [ ] Neon schema creation and chunk storage
- [ ] Ingestion verification script

### Phase 2: Backend Core (Day 2-3)
- [ ] FastAPI scaffold with CORS
- [ ] Environment validation on startup
- [ ] Query routing (selection vs retrieval)
- [ ] Cohere query embedding
- [ ] Qdrant vector search (top_k=5, threshold=0.7)
- [ ] Neon chunk enrichment

### Phase 3: Response Generation (Day 3-4)
- [ ] Gemini 2.5 Flash integration
- [ ] System prompts for retrieval/selection modes
- [ ] Citation enforcement (post-processing)
- [ ] Streaming response implementation
- [ ] Out-of-scope detection

### Phase 4: Frontend Integration (Day 4-5)
- [ ] ChatWidget component
- [ ] Selection capture on submit
- [ ] Session management (localStorage)
- [ ] Streaming response rendering
- [ ] Mobile responsiveness

### Phase 5: Deployment & Hardening (Day 5-6)
- [ ] Dockerfile for HF Spaces
- [ ] Environment secrets configuration
- [ ] Rate limiting (IP-based)
- [ ] Health check endpoint
- [ ] Logging & monitoring
- [ ] Live testing (RAG + selection modes)

---

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research Document | `specs/001-rag-chatbot/research.md` | 🔄 Needs Update |
| Data Model | `specs/001-rag-chatbot/data-model.md` | 🔄 Needs Update |
| API Contract | `specs/001-rag-chatbot/contracts/api-spec.yaml` | 🔄 Needs Update |
| Implementation Plan | `specs/001-rag-chatbot/plan.md` | ✅ Complete (v2) |

---

## Next Steps

1. Run `/sp.tasks` to generate task breakdown from this plan
2. Update `research.md` with Cohere/Gemini decisions
3. Update `data-model.md` with 1024-dimension vectors
4. Update API contracts with new endpoints
5. Begin implementation with ingestion pipeline
6. Use Context7 for each library before writing implementation code

---

## Architectural Decisions Requiring ADRs

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Embedding model | Gemini, Cohere, OpenAI | Cohere embed-english-v3.0 | Better semantic quality, 1024 dims, free tier |
| Response generation | GPT-4, Claude, Gemini | Gemini 2.5 Flash | Fast, cost-effective, good quality |
| Deployment platform | Vercel, Railway, HF Spaces | HuggingFace Spaces | Free Docker hosting, good for ML |
| Vector dimensions | 768 (Gemini), 1024 (Cohere), 1536 (OpenAI) | 1024 | Balance of quality and storage |

**📋 Architectural decision detected**: Embedding and LLM provider selection (Cohere + Gemini)
Document reasoning and tradeoffs? Run `/sp.adr embedding-llm-selection`
