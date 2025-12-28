# Research Document: RAG Chatbot Implementation

**Feature**: 001-rag-chatbot
**Created**: 2025-12-17
**Updated**: 2025-12-23
**Status**: Complete (v2)

---

## 1. Embedding Strategy

### Decision: Use Cohere API (embed-english-v3.0)

**Rationale**:
- Superior semantic quality compared to alternatives
- 1024-dimensional vectors provide good balance of quality and storage
- Free tier provides adequate rate limits (100 calls/min)
- Asymmetric embedding support (`search_document` vs `search_query` input types)
- Well-documented Python SDK with Context7 support

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Gemini embedding-001 | Free, 768 dims | Lower quality for RAG | Rejected |
| Cohere embed-english-v3.0 | High quality, 1024 dims, free tier | External dependency | **Selected** |
| OpenAI text-embedding-3-small | Excellent quality | Paid, adds cost | Rejected (cost) |
| Sentence-transformers (local) | No API costs, full control | Requires GPU, deployment complexity | Rejected (infra) |

**Context7 Verification**:
- Library ID: `/cohere-ai/cohere-python`
- Verified: `client.embed()` with `input_type="search_document"` / `"search_query"`
- Max batch size: 96 texts per call
- Truncation: `truncate="END"` for long inputs

**Risk Level**: Low - Cohere embeddings are production-proven for RAG applications.

---

## 2. Response Generation Strategy

### Decision: Use Google Gemini 2.5 Flash

**Rationale**:
- Fast inference with streaming support
- Cost-effective compared to GPT-4
- Good instruction-following for citation enforcement
- Free tier available for development/testing
- Supports system instructions for grounding

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| GPT-4 / GPT-4o | Best quality | Higher cost, slower | Rejected (cost) |
| Claude 3 Haiku | Good quality, fast | Requires Anthropic account | Rejected |
| Gemini 2.5 Flash | Fast, good quality, free tier | Google ecosystem | **Selected** |
| Llama 3.1 (local) | Free, full control | Deployment complexity, memory | Rejected (infra) |

**Context7 Verification**:
- Library ID: `/googleapis/python-genai`
- Verified: `client.models.generate_content()` and `generate_content_stream()`
- Model: `gemini-2.5-flash`
- Supports: temperature, max_tokens, top_p configuration

**Risk Level**: Low - Gemini 2.5 Flash is well-suited for RAG response generation.

---

## 3. Chunking Strategy

### Decision: Token-based chunking with ~500 tokens, 50-token overlap

**Rationale**:
- Docusaurus build output is HTML, not Markdown
- ~500 tokens provides good semantic granularity
- 50-token overlap maintains context continuity between chunks
- Aligns with Cohere's embedding context window

**Implementation Details**:
- Target chunk size: 500 tokens
- Overlap: 50 tokens between consecutive chunks
- Maximum chunk size: 600 tokens (hard limit)
- Minimum chunk size: 100 tokens (avoid fragments)
- Split priority: `["## ", "### ", "\n\n", ". "]`

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Fixed 512 tokens | Simple, predictable | May break mid-sentence | Modified |
| Header-based only | Preserves semantics | Some sections too large | Rejected |
| Recursive character split | Popular in LangChain | Less semantic awareness | Rejected |
| ~500 tokens + overlap | Good granularity, context | Slightly complex | **Selected** |

**Risk Level**: Low - Token-based chunking with overlap is standard for RAG.

---

## 4. Out-of-Scope Detection

### Decision: Similarity threshold + LLM guardrail

**Rationale**:
- Two-layer approach maximizes accuracy
- Vector similarity threshold (≥0.7) catches obvious misses
- LLM instruction enforces grounding discipline
- Combined approach provides redundancy

**Implementation Details**:
- Layer 1 (Vector): If max similarity score < 0.7, flag as potentially out-of-scope
- Layer 2 (LLM): System prompt includes explicit instruction to decline if context insufficient
- Combine: Low similarity + LLM uncertainty = definitive out-of-scope response

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Similarity threshold only | Fast, simple | False positives on paraphrased queries | Insufficient |
| LLM-only detection | Better semantic understanding | Slower, may still hallucinate | Insufficient |
| Combined approach | High accuracy, redundancy | Slightly more complexity | **Selected** |

**Risk Level**: Medium - Requires tuning threshold after initial deployment.

---

## 5. Grounding Enforcement

### Decision: Enforce at LLM level via system prompt + post-processing

**Rationale**:
- System prompt mandates citation format
- Backend validates citation presence before returning response
- Post-processing adds fallback citation if LLM omits

**Implementation Details**:
- System prompt template includes:
  - Explicit instruction to use ONLY provided context
  - Required citation format: `[Source: {chapter_title}]({url})`
  - Instruction to decline if context insufficient
- Backend post-processing:
  - Validate response contains at least one citation (regex check)
  - If no citation found and context was provided, append fallback citation

**Risk Level**: Low - Standard RAG grounding pattern.

---

## 6. Selected Text Mode Architecture

### Decision: Client-side detection, backend routing

**Rationale**:
- ChatWidget can detect text selection and include in payload
- Backend uses simple conditional: if `context_selection` present → skip vector search
- Clean separation of concerns
- No embedding call needed for selection mode

**Implementation Details**:
- Frontend (ChatWidget):
  - On submit, check if user has text selected via `window.getSelection()`
  - Include in request: `{ query: "...", context_selection: "selected text" | null }`
- Backend routing:
  ```
  if context_selection and context_selection.strip():
      context = context_selection
      source = "user_selection"
      # NO Cohere embedding call
      # NO Qdrant search
  else:
      embedding = cohere.embed(query)
      context = qdrant.search(embedding)
      source = "retrieval"
  ```

**Risk Level**: Low - Straightforward conditional logic.

---

## 7. Rate Limiting Strategy

### Decision: IP-based rate limiting with sliding window

**Rationale**:
- No user auth means IP-based is only option
- Sliding window prevents burst abuse
- Allows normal usage patterns

**Implementation Details**:
- Limits:
  - 30 requests per minute per IP (burst protection)
  - 500 requests per day per IP (daily cap)
- Implementation: `slowapi` library for FastAPI
- Response on limit: 429 with `Retry-After` header

**Risk Level**: Low - Standard rate limiting pattern.

---

## 8. Deployment Platform

### Decision: Hugging Face Spaces with Docker SDK

**Rationale**:
- Free tier with Docker support
- Good for ML/AI applications
- Port 7860 standard for HF Spaces
- Easy environment variable management
- No credit card required

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Vercel | Great DX, edge functions | Python support limited | Rejected |
| Railway | Easy Docker deployment | Free tier limited | Rejected |
| Render | Good free tier | Slow cold starts | Rejected |
| HuggingFace Spaces | Free Docker, ML-focused | 16GB RAM limit | **Selected** |
| AWS Lambda | Scalable | Complex setup, cold starts | Rejected |

**Context7 Verification**:
- Library ID: `/huggingface/huggingface_hub`
- Verified: `api.create_repo(repo_type="space", space_sdk="docker")`
- Supports: secrets management, health checks

**Implementation Details**:
- SDK: Docker
- Port: 7860
- Health check: `/health` endpoint
- Secrets: Via HF Settings > Repository secrets

**Risk Level**: Low - HF Spaces is production-ready for ML APIs.

---

## 9. Conversation Context Management

### Decision: Session-based context with message history in Neon

**Rationale**:
- Follow-up questions need prior context
- Neon provides persistence across requests
- Token budget limits history window
- Session TTL provides automatic cleanup

**Implementation Details**:
- Session: UUID generated client-side, stored in localStorage
- History: Last 5 message pairs (question + answer) from Neon
- Token budget for history: 2000 tokens max
- TTL: 30 minutes idle timeout (cleanup function in Neon)

**Risk Level**: Low - Common pattern for stateless chat backends.

---

## 10. Citation Format Implementation

### Decision: Backend generates citations during response construction

**Rationale**:
- Backend has access to source URLs from Neon
- Gemini receives context with metadata
- Citation format enforced in prompt + post-processing

**Implementation Details**:
- Context passed to Gemini includes:
  ```xml
  <context source="Chapter 5: Kinematics" url="https://book.site/docs/kinematics">
  {chunk_text}
  </context>
  ```
- Gemini instructed to use markdown format: `[Source: Chapter 5: Kinematics](url)`
- Post-processing validates format present

**Risk Level**: Low - Metadata available from Neon lookup.

---

## 11. Dual-Store Synchronization (Qdrant + Neon)

### Decision: Ingestion writes to both atomically, with shared chunk_id

**Rationale**:
- Both stores need same content for different purposes
- Shared UUID enables cross-reference
- Atomic write prevents inconsistency

**Implementation Details**:
- Chunk ID: UUID generated at parse time
- Qdrant: Stores (chunk_id, embedding[1024], minimal metadata)
- Neon: Stores (chunk_id, raw_text, chapter, section, url)
- Query flow:
  1. Cohere embeds query
  2. Qdrant search returns chunk_ids
  3. Neon lookup retrieves full text + URL by chunk_ids

**Risk Level**: Low - Standard dual-store pattern.

---

## 12. CORS Configuration

### Decision: Explicit allow-list for GitHub Pages domain

**Rationale**:
- Security: Don't use wildcard CORS
- Known domain: GitHub Pages URL is predictable
- Easy to configure in FastAPI

**Implementation Details**:
- Allow origins: `["https://{username}.github.io"]`
- Allow methods: `["POST", "GET", "OPTIONS"]`
- Allow headers: `["Content-Type", "X-Session-ID"]`
- Credentials: False (no auth)

**Risk Level**: Low - Standard CORS configuration.

---

## Safe Assumptions

1. **Docusaurus build output structure**: HTML files in `build/docs/` folder
2. **Stable URL structure**: `/docs/{chapter-slug}` pattern
3. **ChatWidget selection API**: Can capture via `window.getSelection()`
4. **HF Spaces Docker**: Supports Python 3.11+ with FastAPI
5. **Free tier adequacy**: Expected usage within limits for all services

## Risky Assumptions (Monitor)

1. **Cohere embedding quality**: May need prompt tuning if retrieval accuracy is poor
2. **3-second latency target**: Depends on cold start behavior on HF Spaces
3. **Qdrant free tier limits**: 1GB storage should be sufficient but monitor
4. **Gemini API latency**: Primary bottleneck for response time
5. **Cohere rate limits**: 100/min may throttle heavy usage

---

## Technology Stack Summary

| Component | Technology | Dimensions/Model | Free Tier |
|-----------|------------|------------------|-----------|
| Embeddings | Cohere | embed-english-v3.0 (1024d) | 100 calls/min |
| Vector Store | Qdrant Cloud | HNSW index | 1GB storage |
| Response Gen | Gemini | 2.5 Flash | Rate varies |
| Backend | FastAPI | 0.115+ | N/A |
| Database | Neon Postgres | Serverless | 512MB |
| Deployment | HF Spaces | Docker SDK | 16GB RAM |

---

## Research Complete

All technical unknowns resolved. Ready to proceed with:
- Phase 1: Ingestion pipeline implementation
- Phase 2: Backend core development
- Phase 3: Response generation integration
- Phase 4: Frontend ChatWidget
- Phase 5: Deployment to HuggingFace Spaces
