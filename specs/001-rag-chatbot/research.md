# Research Document: RAG Chatbot Implementation

**Feature**: 001-rag-chatbot
**Created**: 2025-12-17
**Status**: Complete

## 1. Embedding Strategy

### Decision: Use Gemini API (models/embedding-001)

**Rationale**:
- Mandated by spec constraints (free-tier requirement)
- Gemini embedding-001 produces 768-dimensional vectors
- Sufficient quality for semantic search on educational content
- Free tier provides adequate rate limits for expected usage

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| OpenAI text-embedding-3-small | Higher quality, better semantic understanding | Paid, adds cost | Rejected (cost) |
| Gemini embedding-001 | Free tier, good quality | Slightly lower performance than paid | **Selected** |
| Sentence-transformers (local) | No API costs, full control | Requires GPU, deployment complexity | Rejected (infra) |

**Risk Level**: Low - Gemini embeddings are well-established for RAG applications.

---

## 2. Chunking Strategy

### Decision: Header-based chunking with fallback to token limits

**Rationale**:
- Docusaurus Markdown has clear H1/H2/H3 structure
- Preserves semantic boundaries (sections remain intact)
- Fallback ensures no chunk exceeds embedding context limit

**Implementation Details**:
- Primary split: H2 headers (`##`)
- Secondary split: H3 headers (`###`) if section > 1500 tokens
- Maximum chunk size: 2000 tokens (Gemini embedding limit safety margin)
- Minimum chunk size: 100 tokens (avoid fragments)
- Overlap: 50 tokens between consecutive chunks for context continuity

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Fixed token chunks (512) | Simple, predictable | Breaks mid-sentence, loses context | Rejected |
| Header-based only | Preserves semantics | Some sections too large | Modified |
| Recursive character split | Popular in LangChain | Less semantic awareness | Rejected |
| Header + token hybrid | Best of both | Slightly complex | **Selected** |

**Risk Level**: Low - Header-based is standard for documentation RAG.

---

## 3. Out-of-Scope Detection

### Decision: Similarity threshold + LLM guardrail

**Rationale**:
- Two-layer approach maximizes accuracy
- Vector similarity threshold catches obvious misses
- LLM instruction enforces grounding discipline

**Implementation Details**:
- Layer 1 (Vector): If max similarity score < 0.65, flag as potentially out-of-scope
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

## 4. Grounding Enforcement

### Decision: Enforce at OpenAI Agent level via system prompt

**Rationale**:
- OpenAI Agents SDK provides structured tool use
- System prompt can mandate citation format
- Backend validates citation presence before returning response

**Implementation Details**:
- System prompt template includes:
  - Explicit instruction to use ONLY provided context
  - Required citation format: `[Source: {chapter_title}]({url})`
  - Instruction to decline if context insufficient
- Backend post-processing:
  - Validate response contains at least one citation (regex check)
  - If no citation found and context was provided, append warning

**Risk Level**: Low - Standard RAG grounding pattern.

---

## 5. Selected Text Mode Architecture

### Decision: Client-side detection, backend routing

**Rationale**:
- ChatKit can detect text selection and include in payload
- Backend uses simple conditional: if `context_selection` present → skip vector search
- Clean separation of concerns

**Implementation Details**:
- Frontend (ChatKit):
  - On submit, check if user has text selected
  - Include in request: `{ query: "...", context_selection: "selected text" | null }`
- Backend routing:
  ```
  if context_selection and context_selection.strip():
      context = context_selection
      source = "user_selection"
  else:
      context = vector_search(query)
      source = "retrieval"
  ```

**Risk Level**: Low - Straightforward conditional logic.

---

## 6. Rate Limiting Strategy

### Decision: IP-based rate limiting with sliding window

**Rationale**:
- No user auth means IP-based is only option
- Sliding window prevents burst abuse
- Allows normal usage patterns

**Implementation Details**:
- Limits:
  - 30 requests per minute per IP (burst protection)
  - 500 requests per day per IP (daily cap)
- Storage: In-memory (acceptable for single-instance HF Spaces)
- Response on limit: 429 with `Retry-After` header
- Implementation: `slowapi` library for FastAPI

**Risk Level**: Low - Standard rate limiting pattern.

---

## 7. Conversation Context Management

### Decision: Session-based context with message history window

**Rationale**:
- Follow-up questions need prior context
- Full history would exceed token limits
- Sliding window balances context vs. limits

**Implementation Details**:
- Session: Generated client-side, passed in header
- History window: Last 5 message pairs (question + answer)
- Token budget for history: 2000 tokens max
- Storage: In-memory dict keyed by session_id
- TTL: 30 minutes idle timeout

**Risk Level**: Low - Common pattern for stateless chat backends.

---

## 8. Citation Format Implementation

### Decision: Backend generates citations during response construction

**Rationale**:
- Backend has access to source URLs from Neon
- Agent receives context with metadata
- Citation format enforced in prompt + post-processing

**Implementation Details**:
- Context passed to agent includes:
  ```
  <context source="Chapter 5: Kinematics" url="https://book.site/docs/kinematics">
  {chunk_text}
  </context>
  ```
- Agent instructed to use markdown format: `[Source: Chapter 5: Kinematics](url)`
- Post-processing validates format present

**Risk Level**: Low - Metadata available from Neon lookup.

---

## 9. Dual-Store Synchronization (Qdrant + Neon)

### Decision: Ingestion writes to both atomically, with shared chunk_id

**Rationale**:
- Both stores need same content for different purposes
- Shared ID enables cross-reference
- Atomic write prevents inconsistency

**Implementation Details**:
- Chunk ID: UUID generated at parse time
- Qdrant: Stores (chunk_id, embedding, minimal metadata)
- Neon: Stores (chunk_id, raw_text, chapter_title, section_title, url)
- Query flow:
  1. Vector search returns chunk_ids
  2. Neon lookup retrieves full text + URL by chunk_ids

**Risk Level**: Low - Standard dual-store pattern.

---

## 10. CORS Configuration

### Decision: Explicit allow-list for GitHub Pages domain

**Rationale**:
- Security: Don't use wildcard CORS
- Known domain: GitHub Pages URL is predictable
- Easy to configure in FastAPI

**Implementation Details**:
- Allow origins: `["https://{username}.github.io"]`
- Allow methods: `["POST", "OPTIONS"]`
- Allow headers: `["Content-Type", "X-Session-ID"]`
- Credentials: False (no auth)

**Risk Level**: Low - Standard CORS configuration.

---

## Safe Assumptions

1. **Docusaurus Markdown structure**: Book uses standard H1/H2/H3 headers ✅
2. **Stable URL structure**: `/docs/{chapter-slug}` pattern ✅
3. **ChatKit selection API**: Can capture and transmit selected text ✅
4. **HF Spaces Docker**: Supports Python 3.10+ with FastAPI ✅
5. **Free tier adequacy**: Expected usage within limits ✅

## Risky Assumptions (Monitor)

1. **Gemini embedding quality**: May need prompt tuning if retrieval poor
2. **3-second latency target**: Depends on cold start behavior on HF Spaces
3. **Qdrant free tier limits**: 1GB storage should be sufficient but monitor
4. **OpenAI API latency**: Primary bottleneck for response time

---

## Research Complete

All technical unknowns resolved. Ready to proceed with:
- Phase 1: Data model and API contracts
- Phase 2: Implementation planning
