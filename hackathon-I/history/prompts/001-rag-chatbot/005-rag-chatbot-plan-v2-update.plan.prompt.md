---
id: 005
title: RAG Chatbot Plan v2 Update
stage: plan
date: 2025-12-23
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: user
command: /sp.plan
labels: ["rag", "chatbot", "cohere", "gemini", "huggingface", "plan", "architecture"]
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
  - null
---

## Prompt

/sp.plan

Update the plan.md file for this feature to implement a RAG system:
1. Content Ingestion & Chunking:
   - Extract textual content from Docusaurus build folder (HTML output)
   - Parse HTML to extract meaningful text blocks (paragraphs, headers, code blocks)
   - Chunk content intelligently (~500 tokens per chunk with 50-token overlap)
   - Track source metadata (chapter, section, URL, heading hierarchy)
2. Embedding Pipeline:
   - Use Cohere API for embedding generation (model: embed-english-v3.0)
   - Store embeddings in Qdrant Cloud with HNSW index
   - Create embedding for each chunk with consistent dimensionality
   - Include metadata payload (chapter, section, URL) in Qdrant points
3. Retrieval Flow:
   - Embed user query using same Cohere model (search_query input type)
   - Perform similarity search in Qdrant (top_k=5, score threshold ≥0.7)
   - Apply optional reranking based on query-chunk relevance
   - Return retrieved chunks with source attribution
4. Selected-Text-Only Mode:
   - ChatWidget captures user's text selection (ChatKit SDK)
   - When selection exists, send selected text as context
   - Backend skips vector search entirely in selection mode
   - Still generates response via LLM but without RAG retrieval
5. Response Generation:
   - Use Gemini-2.5-Flash for response synthesis
   - Construct citation-aware prompts with retrieved context
   - Include source links in responses (markdown format)
   - Support streaming responses via SSE
6. Backend Architecture:
   - FastAPI application with the following endpoints:
     - POST /chat - main query endpoint (handles both modes)
     - POST /selected-text-query - explicit selection-only endpoint
     - GET /health - dependency health check
   - Environment-based configuration (API keys, URLs)
   - Structured logging with request tracing
7. Session & Persistence:
   - Neon Serverless PostgreSQL for chat history
   - Session management with UUID tracking
   - Message history for follow-up questions (last 5 Q&A pairs)
   - TTL-based session cleanup (30 min idle)
8. Deployment:
   - Hugging Face Spaces with Docker SDK
   - Port 7860 (HF standard)
   - Health endpoint for monitoring
   - CORS configuration for GitHub Pages origin
9. Configuration & Testing:
   - Document all required environment variables
   - Include rate limiting (IP-based, 30 req/min)
   - Integration test strategy

Use Context7 strictly for all documentation references.

## Response snapshot

Successfully updated all planning artifacts for RAG Chatbot v2 implementation:

**1. plan.md** - Complete rewrite with:
- Architecture diagram showing dual-store pattern (Qdrant + Neon)
- 12 detailed implementation sections with code scaffolding
- Technology stack: Cohere embed-english-v3.0 (1024 dims), Gemini 2.5 Flash, HF Spaces
- Code patterns for CohereEmbedder, QdrantStore, GeminiGenerator classes
- FastAPI endpoint implementations with streaming support
- System prompt template for citation enforcement

**2. research.md** - Updated technology decisions:
- Embedding: Cohere embed-english-v3.0 (selected over Gemini embedding-001)
- Response Gen: Gemini 2.5 Flash (selected over GPT-4)
- Deployment: HuggingFace Spaces Docker SDK (selected over Vercel/Railway)
- Context7 verification for all library IDs

**3. data-model.md** - Schema updates:
- Vector dimensions: 768 → 1024 (Cohere)
- ChunkEmbedding Qdrant collection with HNSW config
- Migration notes from v1 to v2

**4. api-spec.yaml** - Contract updates:
- Version: 2.0.0
- New `/chat/stream` SSE endpoint
- New `/selected-text-query` endpoint
- Updated health response with Cohere service status

**Context7 Libraries Researched:**
- `/cohere-ai/cohere-python` - embed() with input_type param
- `/qdrant/qdrant-client` - upsert, search, collection creation
- `/googleapis/python-genai` - generate_content_stream()
- `/huggingface/huggingface_hub` - Spaces deployment patterns

## Outcome

- ✅ Impact: Complete v2 architecture plan ready for implementation
- 🧪 Tests: No tests (planning phase)
- 📁 Files: 4 files updated (plan.md, research.md, data-model.md, api-spec.yaml)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation task breakdown
- 🧠 Reflection: Context7 was essential for verifying current API patterns; Cohere's asymmetric embedding (search_document vs search_query) is critical for RAG quality

## Evaluation notes (flywheel)

- Failure modes observed: None - Context7 successfully resolved all library documentation
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement ingestion pipeline first to validate chunking strategy
