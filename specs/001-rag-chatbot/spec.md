# Feature Specification: Integrated RAG Chatbot for AI-Native Book

**Feature Branch**: `001-rag-chatbot`
**Created**: 2025-12-17
**Updated**: 2025-12-17
**Status**: Draft
**Input**: User description: "Build a Retrieval-Augmented Generation (RAG) chatbot embedded in an AI-native book that answers reader questions using only the book's content."

## Clarifications

### Session 2025-12-17

- Q: What is the behavior when selected text is empty or whitespace-only? → A: Treat as no selection but provide subtle user feedback to indicate the selection was ignored
- Q: What rate limiting strategy should be implemented to ensure free-tier compliance? → A: Implement per-user/IP rate limiting with reasonable daily/monthly quotas to prevent abuse while allowing normal usage

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask Question About Book Content (Priority: P1)

A reader encounters a concept in the book they want to understand better. They open the chatbot interface and type a question about a topic covered in the book. The chatbot retrieves relevant passages from the book content and generates a concise, accurate answer that references the specific chapter or section where the information is found, with clickable links to the source.

**Why this priority**: This is the core value proposition of the chatbot. Without the ability to answer questions accurately from book content, the feature has no utility.

**Independent Test**: Can be fully tested by asking a question about a known topic in the book and verifying the response is accurate, relevant, and includes a clickable reference link to the correct source section.

**Acceptance Scenarios**:

1. **Given** the reader is on any page of the book with the chatbot visible, **When** they type "What is inverse kinematics?" and submit, **Then** the chatbot returns an accurate explanation based on book content within 3 seconds, including a markdown link reference in format `[Source: Chapter Name](URL)`.
2. **Given** the reader asks a question about a topic covered in multiple chapters, **When** they submit the question, **Then** the chatbot synthesizes information from relevant sections and provides appropriate clickable references to each source.
3. **Given** the reader asks a follow-up question, **When** they submit it, **Then** the chatbot considers the conversation context to provide a relevant response.

---

### User Story 2 - Ask Question Using Selected Text (Priority: P1)

A reader highlights a specific passage in the book that they find confusing or want more information about. They then ask a question, and the chatbot uses **ONLY** the selected text as context for answering, providing explanations or elaborations specific to that passage without searching for additional content.

**Why this priority**: Selected text context is a key differentiator that makes the chatbot contextually aware of what the reader is currently focused on. Using only the selected text ensures precise, focused answers.

**Independent Test**: Can be tested by selecting a passage, asking a related question, and verifying the response directly addresses ONLY the selected text without incorporating unrelated book content.

**Acceptance Scenarios**:

1. **Given** the reader has selected a paragraph about "motor control algorithms", **When** they ask "Can you explain this in simpler terms?", **Then** the chatbot uses ONLY the selected text as context and provides a simplified explanation of that specific content (no vector search performed).
2. **Given** the reader has selected a code example, **When** they ask "What does this code do?", **Then** the chatbot explains ONLY the selected code without retrieving additional book context.
3. **Given** the reader has selected text and asks any question, **When** they submit, **Then** the system MUST ground the answer exclusively in the selected text, bypassing semantic search entirely.

---

### User Story 3 - Handle Out-of-Scope Questions (Priority: P2)

A reader asks a question about a topic not covered in the book. The chatbot recognizes that the question cannot be answered using the book's content and responds gracefully, informing the reader that the topic is outside the book's scope, potentially suggesting related topics that are covered.

**Why this priority**: Graceful handling of out-of-scope questions maintains user trust and sets appropriate expectations. Users need clear feedback when their question cannot be answered.

**Independent Test**: Can be tested by asking a question about a topic definitely not in the book and verifying the chatbot declines appropriately.

**Acceptance Scenarios**:

1. **Given** the reader asks "What is the stock price of Tesla?", **When** they submit, **Then** the chatbot responds that this question is outside the book's scope and does not attempt to answer it.
2. **Given** the reader asks about a related but uncovered topic, **When** they submit, **Then** the chatbot indicates the topic isn't covered but suggests related topics from the book that might be helpful.
3. **Given** the reader asks a partially answerable question, **When** they submit, **Then** the chatbot answers the portion that can be addressed using book content and clearly indicates what cannot be answered.

---

### User Story 4 - Access Chatbot on Mobile Device (Priority: P2)

A reader accesses the AI-native book on their mobile device and wants to use the chatbot. The chatbot interface is responsive and usable on smaller screens, allowing mobile readers the same functionality as desktop users.

**Why this priority**: Mobile accessibility ensures the feature reaches all target users. However, core functionality (P1) must work first before optimizing for different devices.

**Independent Test**: Can be tested by accessing the chatbot on a mobile device and completing a basic question-answer flow.

**Acceptance Scenarios**:

1. **Given** the reader opens the book on a mobile device, **When** they access the chatbot, **Then** the interface is usable and text is readable without horizontal scrolling.
2. **Given** the reader types a question on mobile, **When** they submit, **Then** the response displays correctly and is easy to read on a small screen.
3. **Given** the reader wants to select text on mobile, **When** they perform the standard mobile text selection gesture, **Then** they can use the selected text with the chatbot.

---

### User Story 5 - Content Ingestion for Book Updates (Priority: P3)

When book content is updated or a new chapter is added, the system administrator runs an ingestion process that parses the book's source files, chunks content by headers/sections, and populates both the content store (raw text, metadata, URLs) and the vector store (embeddings) to keep the chatbot knowledge current.

**Why this priority**: Ingestion is a prerequisite for the chatbot to function but is a one-time/periodic administrative task, not a user-facing feature.

**Independent Test**: Can be tested by adding a new chapter to the book source, running the ingestion process, and verifying the chatbot can answer questions about the new content.

**Acceptance Scenarios**:

1. **Given** new book content exists in the source format, **When** the ingestion script is executed, **Then** the content is chunked by headers, stored with chapter/section metadata and URLs, and embeddings are generated and stored.
2. **Given** existing content has been modified, **When** ingestion runs, **Then** the updated content replaces the old version in both stores.
3. **Given** ingestion completes successfully, **When** a user asks about newly ingested content, **Then** the chatbot can retrieve and answer based on that content.

---

### Edge Cases

- What happens when the reader asks a question in a language other than English?
  - The chatbot responds in the same language if the book content is available in that language; otherwise, it indicates content is only available in the book's primary language.
- How does the system handle very long questions (>500 characters)?
  - The system accepts and processes the question but may truncate for display purposes; a character limit indicator is shown to users.
- What happens when network connectivity is lost mid-conversation?
  - The chatbot displays a clear error message and retains the conversation history locally so users can retry when connection is restored.
- How does the system handle concurrent questions from the same user?
  - Questions are queued and processed sequentially to maintain conversation coherence.
- What happens when the vector store is temporarily unavailable?
  - The chatbot returns a friendly error message asking the user to try again shortly, without exposing technical details.
- What happens when selected text is provided but is empty or whitespace-only?
  - The system treats this as no selection and falls back to semantic search mode, with subtle user feedback indicating the selection was ignored.
- What happens if the metadata store is unavailable but vector store works?
  - The system returns a degraded response indicating source links are temporarily unavailable.
- What happens when a user exceeds rate limits?
  - The system returns a rate limit exceeded error with a polite message and time until reset.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chat Functionality
- **FR-001**: System MUST accept natural language questions from readers through the embedded chat interface.
- **FR-002**: System MUST generate responses that are grounded in and derived from book content only.
- **FR-003**: System MUST include chapter or section references as clickable markdown links in format `[Source: Chapter Name](URL)`.
- **FR-004**: System MUST maintain conversation context within a session to support follow-up questions.
- **FR-005**: System MUST provide responses within 3 seconds under normal operating conditions.

#### Selected Text Behavior (Strict Constraint)
- **FR-006**: When user-selected text is provided as context, the system MUST use ONLY that text for grounding the answer.
- **FR-007**: When user-selected text is provided, the system MUST NOT perform any semantic/vector search.
- **FR-008**: The chat interface MUST transmit user-selected text as a distinct context payload to the backend.
- **FR-009**: When user-selected text is empty or whitespace-only, the system MUST treat as no selection and provide subtle user feedback.

#### Semantic Search Behavior (No Selection)
- **FR-010**: When NO selected text is provided, the system MUST generate an embedding for the user query.
- **FR-011**: When NO selected text is provided, the system MUST perform similarity search against stored book content embeddings.
- **FR-012**: When NO selected text is provided, the system MUST retrieve full text and source URL from the metadata store for matched content.

#### Out-of-Scope Handling
- **FR-013**: System MUST identify when a question cannot be adequately answered using book content and respond accordingly.
- **FR-014**: System MUST decline to answer questions clearly outside the book's scope with a helpful message.

#### Content Ingestion
- **FR-015**: System MUST provide an ingestion mechanism that parses book source files (Markdown format).
- **FR-016**: Ingestion MUST chunk content by headers/sections to preserve logical boundaries.
- **FR-017**: Ingestion MUST generate embeddings for each chunk and store them in the vector store.
- **FR-018**: Ingestion MUST store raw text, chapter titles, and source URLs in the metadata store.

#### Cross-Origin & Integration
- **FR-019**: Backend MUST accept requests from the frontend hosting domain (cross-origin).
- **FR-020**: System MUST work on both desktop and mobile browsers without requiring different access methods.
- **FR-021**: System MUST handle errors gracefully, displaying user-friendly messages without exposing technical details.

#### Rate Limiting & Usage Control
- **FR-022**: System MUST implement per-user/IP rate limiting to prevent abuse and ensure free-tier compliance.
- **FR-023**: System MUST return appropriate rate limit exceeded messages when quotas are exceeded.

### Key Entities

- **Book Content Chunk**: A discrete segment of book content (paragraph or section) stored with:
  - Raw text content
  - Chapter title
  - Section title
  - Source URL (link to the page in the book)
  - Vector embedding (stored separately in vector store)

- **Conversation Session**: A sequence of questions and responses from a single reader, maintaining context for follow-up questions within the session.

- **Selected Text Context**: User-highlighted text from the book that serves as the EXCLUSIVE context for a question (when provided).

- **Query Context**: Either selected text (exclusive mode) OR retrieved chunks from semantic search (search mode) - never both simultaneously.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% adherence to "Selected Text" constraint - when context selection is provided, zero semantic searches are performed.
- **SC-002**: End-to-end response time is 3 seconds or less (including network latency, embedding generation, search, and response generation).
- **SC-003**: At least 90% of evaluated answers are factually correct and grounded in book content (measured via manual evaluation of sample queries).
- **SC-004**: Out-of-scope questions are correctly identified and declined at least 90% of the time.
- **SC-005**: All chatbot responses containing book references include properly formatted clickable markdown links.
- **SC-006**: The chatbot interface is functional and usable on screens as small as 320px wide (mobile minimum).
- **SC-007**: System operates within free-tier usage limits for all external services without service interruption.
- **SC-008**: Ingestion script successfully processes 100% of valid book source files without data loss.
- **SC-009**: System implements effective rate limiting that prevents abuse while allowing normal usage patterns.

## Scope Boundaries

### In Scope

- Question answering using book content only
- Selected text as EXCLUSIVE context input (bypasses search)
- Semantic search for questions without selected text
- Chapter/section references as clickable markdown links
- Conversational follow-up support within a session
- Desktop and mobile web interface
- Graceful out-of-scope handling
- Content ingestion from book source files
- Cross-origin request support from frontend domain
- Rate limiting to ensure free-tier compliance

### Out of Scope

- General AI tutoring beyond book content
- Image, audio, or video understanding or generation
- User authentication or personalization
- Conversation history persistence across sessions
- Analytics, dashboards, or user tracking
- Any paid API or service usage
- Multi-language support beyond the book's primary language
- Real-time content synchronization (ingestion is manual/batch)

## Assumptions

- The book content is available in Markdown format (Docusaurus-compatible) suitable for parsing and chunking.
- The book has clear header structure (H1, H2, H3) that can be used for chunking and section identification.
- Each book page/chapter has a stable, predictable URL structure for generating source links.
- The frontend chat component can capture and transmit user text selections.
- Free-tier limits of all external services are sufficient for expected usage patterns.
- The target browsers are modern evergreen browsers (Chrome, Firefox, Safari, Edge) from the last 2 years.
- The book content fits within the storage limits of free-tier vector and metadata stores.

## Dependencies

### Backend Services
- **Hugging Face Spaces**: Deployment platform for backend API (Docker container, port 7860)
- **Qdrant Cloud Free Tier**: Vector database for storing and querying content embeddings
- **Neon Serverless Postgres**: Metadata store for raw book text, chapter titles, and source URLs
- **Gemini API (models/embedding-001)**: Embedding generation for all vector operations
- **OpenAI API**: Response generation (via Agents SDK orchestration)

### Frontend Services
- **GitHub Pages**: Hosting platform for the Docusaurus book site
- **OpenAI ChatKit**: Frontend chat UI component embedded in the book

### Content
- **Book Source Files**: Docusaurus Markdown files as the authoritative content source

## Technical Constraints

These constraints are mandated by the hackathon requirements:

1. **Selected Text Rule**: When `context_selection` payload is present, backend MUST use only that text - no vector search.
2. **Citation Format**: All source references MUST use markdown link format: `[Source: Chapter Name](URL)`
3. **CORS Policy**: Backend MUST explicitly allow requests from the GitHub Pages domain.
4. **Free Tier Only**: All services must operate within free-tier limits (no paid upgrades).
5. **Port Constraint**: Backend runs on port 7860 (Hugging Face Spaces requirement).
