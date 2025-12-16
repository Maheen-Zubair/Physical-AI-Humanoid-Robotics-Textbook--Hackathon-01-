<!--
  ============================================================================
  SYNC IMPACT REPORT
  ============================================================================
  Version change: 1.0.0 → 2.0.0 (MINOR - added Phase 2 RAG Chatbot scope)

  Modified principles:
  - Project title: "AI / Spec-Driven Book Creation" → "AI/Spec-Driven Book with Integrated RAG Chatbot"

  Added sections:
  - Phase 2 Core Principles (VI-IX): Chatbot Accuracy, Chatbot Clarity,
    Reproducibility, Rigor
  - Phase 2 Technical Standards
  - Phase 2 Technical Constraints (performance, stack)
  - Phase 2 Success Criteria

  Removed sections: None

  Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check covers both phases)
  - .specify/templates/spec-template.md: ✅ Compatible (user stories support chatbot features)
  - .specify/templates/tasks-template.md: ✅ Compatible (phase structure supports chatbot tasks)

  Follow-up TODOs: None
  ============================================================================
-->

# AI/Spec-Driven Book with Integrated RAG Chatbot Constitution

This project consists of two unified phases:
1. **Phase 1**: AI/Spec-Driven Book Creation
2. **Phase 2**: Integrated RAG Chatbot Development

---

## Phase 1: Book Creation Core Principles

### I. Spec-Driven Writing

All book content MUST strictly follow approved specs, plans, and tasks.

- Every chapter MUST be generated based on the book specification only
- No content outside the defined book scope is permitted
- Each chapter MUST map to a defined module or section in the book spec
- Changes to content require corresponding updates to specs first

**Rationale**: Ensures traceability and prevents scope creep. Every piece of content has a clear origin in the planning artifacts.

### II. Accuracy

Technical explanations MUST be correct and aligned with official documentation and standards.

- Technical claims MUST be verifiable using official docs or trusted sources
- Code examples MUST be correct, executable, and produce expected results
- References to external tools, frameworks, or APIs MUST match their current behavior
- When in doubt, verify against authoritative sources before publishing

**Rationale**: Educational content loses value if it contains errors. Learners build on what they read—incorrect foundations lead to compounding mistakes.

### III. Clarity

Content MUST be written in simple, beginner-friendly English.

- Use plain language; avoid unnecessary jargon
- When technical terms are required, define them on first use
- Sentences should be direct and concise
- Complex concepts MUST be broken down into digestible parts
- Target audience: Beginner to intermediate learners

**Rationale**: The goal is education, not demonstration of expertise. If a reader cannot understand the content, the content has failed.

### IV. Consistency

Terminology, structure, and tone MUST remain consistent across all chapters.

- Use the same term for the same concept throughout the book
- Maintain uniform heading hierarchy and formatting
- Keep instructional tone consistent (second person "you" for instructions)
- Follow established patterns for code examples, diagrams, and callouts

**Rationale**: Consistency reduces cognitive load. Readers should focus on learning concepts, not adapting to varying styles.

### V. Educational Focus

The book MUST explain concepts step-by-step with practical examples.

- Start with "why" before "how"
- Build complexity gradually—prerequisites before advanced topics
- Include working examples that readers can follow along with
- Provide exercises or checkpoints where appropriate
- Connect new concepts to previously learned material

**Rationale**: Effective teaching requires scaffolding. Each concept should build naturally on what came before.

---

## Phase 2: RAG Chatbot Core Principles

### VI. Chatbot Accuracy

Chatbot answers MUST reflect book content correctly.

- Responses MUST be grounded in the book's actual text
- No hallucinations or fabricated information permitted
- Answers MUST cite or reference the source section when possible
- If the book does not contain relevant information, the chatbot MUST indicate this

**Rationale**: The chatbot extends the book's educational value. Incorrect answers undermine trust and learning.

### VII. Chatbot Clarity

Responses MUST be concise, understandable, and relevant.

- Answers MUST directly address the user's question
- Response length MUST be appropriate to the query complexity
- Technical terms MUST be explained if not defined in context
- Avoid verbose or tangential responses

**Rationale**: Users expect quick, helpful answers. Unclear responses defeat the chatbot's purpose.

### VIII. Reproducibility

Chatbot queries and answers MUST be traceable to source content.

- Every response MUST be derivable from the indexed book content
- Query-answer pairs SHOULD be logged for quality review
- Embeddings and retrieval logic MUST be deterministic given the same input
- Version the book content that the chatbot is trained on

**Rationale**: Traceability enables debugging, quality assurance, and continuous improvement.

### IX. Rigor

Only text from the book or user-selected text is used for responses.

- Chatbot MUST NOT pull information from external sources
- User-selected text queries MUST be bounded to the book's content
- Plagiarism check: 0% tolerance for content reuse outside the book
- RAG retrieval MUST use only the indexed book embeddings

**Rationale**: The chatbot is a book companion, not a general-purpose assistant. Scope discipline ensures quality.

---

## Phase 1: Content Standards

### Writing Requirements

- **Format**: All content MUST be Markdown (.md) files
- **Structure**: Headings and organization MUST be compatible with Docusaurus
- **Code Examples**: MUST be correct, readable, and include explanatory comments
- **Language**: Simple English with no unnecessary jargon
- **Style**: Clear, concise, and instructional

### Quality Gates

- [ ] Content follows approved spec for the chapter/section
- [ ] Technical claims are verifiable against official sources
- [ ] Code examples execute without errors
- [ ] Language is appropriate for beginner-to-intermediate audience
- [ ] Terminology is consistent with rest of book
- [ ] Markdown renders correctly in Docusaurus

---

## Phase 2: Technical Standards

### Code Requirements

- Code MUST follow best practices for the stack:
  - **Backend**: FastAPI
  - **Database**: Neon Postgres
  - **Vector Store**: Qdrant
  - **AI Integration**: OpenAI Agents / ChatKit SDKs
- All code MUST be readable, well-documented, and tested
- API endpoints MUST include error handling and validation

### Chatbot Quality Gates

- [ ] Responses match book content accurately
- [ ] No hallucinations or fabricated information
- [ ] Source citations included where applicable
- [ ] Response latency < 2 seconds
- [ ] Concurrent query handling ≥ 100 users

---

## Technical Constraints

### Phase 1: Book Platform

| Constraint | Value |
|------------|-------|
| Output Format | Markdown (.md) |
| Documentation Framework | Docusaurus |
| Deployment Target | GitHub Pages |
| Audience Level | Beginner to intermediate |
| Language | Simple English |

### Phase 2: Chatbot Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| Database | Neon Postgres |
| Vector Database | Qdrant |
| AI/LLM Integration | OpenAI Agents / ChatKit SDKs |
| Frontend Integration | Embedded in Docusaurus |
| Deployment | GitHub Pages compatible |

### Phase 2: Performance Requirements

| Metric | Requirement |
|--------|-------------|
| Concurrent Queries | ≥ 100 |
| Query Latency | < 2 seconds |
| Availability | 99.5% uptime |

---

## Success Criteria

### Phase 1: Book

- The full book MUST build successfully in Docusaurus without errors
- All content MUST strictly follow approved specs, plans, and tasks
- No unrelated or off-topic content is present
- All code examples MUST execute correctly
- Navigation and cross-references MUST function properly

### Phase 2: Chatbot

- Chatbot MUST be functional and correctly answer questions
- Responses MUST match book content accurately
- Embedded chatbot MUST work on GitHub Pages without errors
- Claude Code / Spec-Kit Plus workflow MUST be used to generate and integrate
- Integration with Phase 1 content MUST be seamless

### Combined Success

- Both phases integrated into a single deployable Docusaurus site
- Users can read book content AND query the chatbot from the same interface
- All quality gates pass for both phases

---

## Governance

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Changes to principles require review and explicit approval
3. All amendments MUST include a migration plan for affected content
4. Version number MUST be updated following semantic versioning

### Versioning Policy

- **MAJOR**: Principle removal, redefinition, or backward-incompatible changes
- **MINOR**: New principle added, section expanded, or new guidance introduced
- **PATCH**: Clarifications, typo fixes, or non-semantic refinements

### Compliance

- All PRs MUST verify compliance with this constitution
- The Constitution Check in plan.md MUST pass before implementation
- Deviations require explicit justification and approval
- Both phases must pass their respective quality gates

**Version**: 2.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
