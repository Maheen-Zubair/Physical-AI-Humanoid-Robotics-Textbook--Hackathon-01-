---
id: 001
title: Add RAG Chatbot Phase to Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "amendment", "rag-chatbot", "phase-2", "fastapi", "qdrant"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

update this file ->/sp.prompt

# Project: AI/Spec-Driven Book with Integrated RAG Chatbot

## Instructions

You are tasked with creating a **unified project** consisting of **two phases**:
1. **AI/Spec-Driven Book Creation**
2. **Integrated RAG Chatbot Development**

Follow the Constitution guidelines exactly, and generate outputs for each phase.

---

## Phase 1 – AI/Spec-Driven Book Creation

**Core Principles:**
- Accuracy through verified sources for all book content
- Clarity for target audienceters ready to deploy on Docusaurus.

---

## Phase 2 – Integrated RAG Chatbot Development

**Core Principles:**
- Accuracy: Chatbot answers must reflect book content correctly
- Clarity: Responses must be concise, understandable, and relevant
- Reproducibility: Chatbot queries and answers must be traceable to the source content
- Rigor: Only text from the book or user-selected text is used

**Key Standards:**
- Chatbot must answer based only on selected book content
- Responses concise, relevant, and contextually accurate
- Code and queries must follow best practices for OpenAI Agents / ChatKit SDKs, FastAPI, Neon Postgres, and Qdrant
- Plagiarism check: 0% tolerance for content reuse outside the book

**Constraints:**
- Chatbot must support at least 100 concurrent queries
- Latency: < 2 seconds per query
- Embedded within the published Docusaurus book
- Integration with Phase 1 content seamless and functional

**Success Criteria:**
- Chatbot functional and correctly answering questions
- Responses match book content accurately
- Embedded chatbot works on GitHub Pages with no errors
- Claude Code / Spec-Kit Plus workflow used effectively to generate and integrate the chatbot

**Tasks for Phase 2:**
1. Design a **chatbot architecture** using OpenAI Agents / ChatKit SDKs, FastAPI, Neon Postgres, and Qdrant.
2. Define how the chatbot will **ingest book content** and **answer user-selected text queries**.
3. Generate code templates for the backend, database, and embeddings.
4. Provide instructions for **embedding the chatbot** in Docusaurus pages.
5. Test workflow: generate sample questions and ensure accurate answers.

---

**Output Requirements:**
- Phase 1: Complete Markdown files ready for Docusaurus deployment
- Phase 2: Backend code, database schema, embedding scripts, and chatbot integration instructions
- Both phases: Detailed steps, references, and examples included

---

**End of Prompt**

## Response snapshot

Updated constitution from v1.0.0 to v2.0.0. Added Phase 2 (RAG Chatbot Development) with four new principles:

- **VI. Chatbot Accuracy**: Responses must reflect book content correctly
- **VII. Chatbot Clarity**: Concise, understandable, relevant responses
- **VIII. Reproducibility**: Traceable queries and answers
- **IX. Rigor**: Only book content used, no external sources

Added technical standards for the chatbot stack (FastAPI, Neon Postgres, Qdrant, OpenAI Agents/ChatKit SDKs) and performance requirements (100 concurrent queries, <2s latency).

Combined success criteria ensure both phases integrate into a single Docusaurus deployment with embedded chatbot.

## Outcome

- Impact: Constitution expanded to cover unified two-phase project scope
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md updated
- Next prompts: /sp.specify to create book and chatbot specifications
- Reflection: Version bump to 2.0.0 reflects significant scope expansion while preserving all Phase 1 principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
