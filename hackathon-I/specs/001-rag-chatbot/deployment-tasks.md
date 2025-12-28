# Tasks: RAG Chatbot Hugging Face Spaces Deployment

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, DEPLOYMENT_CHECKLIST.md
**Context**: Backend deployment to Hugging Face Spaces (Docker SDK)

**User Context**:
- Has Hugging Face account ✅
- All API keys ready ✅
- Qdrant collection populated ✅
- Deploying backend only (Option A)

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths and commands in descriptions

---

## Phase 1: Pre-Deployment Setup

**Purpose**: Prepare local environment and gather required credentials

- [ ] T001 Collect HF username and create HF write token at https://huggingface.co/settings/tokens
- [ ] T002 [P] Verify all API keys are available and working:
  - `QDRANT_URL` - Qdrant Cloud cluster URL
  - `QDRANT_API_KEY` - Qdrant API key
  - `DATABASE_URL` - Neon Postgres connection string
  - `COHERE_API_KEY` - Cohere API key for embeddings
  - `GEMINI_API_KEY` - Google Gemini API key
- [ ] T003 [P] Install Hugging Face CLI: `pip install huggingface_hub`
- [ ] T004 Login to Hugging Face CLI: `huggingface-cli login` (enter write token when prompted)
- [ ] T005 Determine production values for:
  - `BOOK_BASE_URL` - Your GitHub Pages book URL (e.g., `https://maheen-zubair.github.io/Physical-AI-Humanoid-Robotics-Textbook--Hackathon-01-/docs`)
  - `CORS_ORIGINS` - JSON array of allowed origins (e.g., `["https://maheen-zubair.github.io"]`)

**Checkpoint**: All credentials collected and HF CLI authenticated

---

## Phase 2: HF Spaces Configuration Files

**Purpose**: Create and configure files required for HF Spaces Docker deployment

### 2.1 Create HF Spaces README (Required Metadata)

- [ ] T006 Create `chatbot/README.md` with HF Spaces metadata:
```markdown
---
title: RAG Chatbot API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# RAG Chatbot API

Retrieval-Augmented Generation chatbot for the Physical AI & Humanoid Robotics textbook.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root health check |
| `/api/health` | GET | Detailed health status |
| `/api/chat` | POST | Chat with book context |
| `/api/chat/stream` | POST | Streaming chat (SSE) |
| `/api/chat/selection` | POST | Ask about selected text |

## Environment Variables

This Space requires secrets (set in Settings > Repository secrets):
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `DATABASE_URL`
- `COHERE_API_KEY`
- `GEMINI_API_KEY`
- `BOOK_BASE_URL`
- `CORS_ORIGINS`
```

### 2.2 Update Dockerfile for HF Spaces

- [ ] T007 Update `chatbot/Dockerfile` to ensure HF Spaces compatibility:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# HuggingFace Spaces expects port 7860
EXPOSE 7860

# Health check for HF Spaces
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Run the application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 2.3 Verify Requirements File

- [ ] T008 Verify `chatbot/requirements.txt` includes all dependencies:
```
fastapi>=0.104.1
qdrant-client>=1.8.0
cohere>=5.11.0
google-genai>=0.3.0
pydantic>=2.5.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
asyncpg>=0.29.0
slowapi>=0.1.9
python-frontmatter>=1.0.0
tiktoken>=0.5.1
httpx>=0.27.0
```

### 2.4 Create .gitignore for HF Space

- [ ] T009 Create `chatbot/.gitignore` to exclude sensitive/unnecessary files:
```
.env
.env.*
!.env.example
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
venv/
*.log
.DS_Store
```

**Checkpoint**: All HF Spaces configuration files ready

---

## Phase 3: Code Updates for Production

**Purpose**: Update code for production deployment

### 3.1 Update CORS for Production

- [ ] T010 Update `chatbot/app/main.py` to include production CORS origins:
  - Ensure GitHub Pages URL is in allowed origins
  - Keep localhost for development testing
  - Format: Add production URL to `cors_origins` list

### 3.2 Environment Variable Validation

- [ ] T011 Verify `chatbot/app/config.py` validates all required environment variables on startup:
  - `QDRANT_URL`
  - `QDRANT_API_KEY`
  - `DATABASE_URL`
  - `COHERE_API_KEY`
  - `GEMINI_API_KEY`
  - `BOOK_BASE_URL`
  - `CORS_ORIGINS` (with sensible default)

### 3.3 Health Check Enhancement

- [ ] T012 [P] Verify `chatbot/app/routers/health.py` includes service status checks:
  - Qdrant connection status
  - Database connection status
  - Return structured JSON with service statuses

### 3.4 Remove Debug/Development Code

- [ ] T013 [P] Review and remove any debug print statements or development-only code in:
  - `chatbot/app/main.py`
  - `chatbot/app/routers/chat.py`
  - `chatbot/app/services/*.py`

**Checkpoint**: Code ready for production deployment

---

## Phase 4: Create Hugging Face Space

**Purpose**: Create and configure the HF Space

- [ ] T014 Create new HF Space using CLI:
```bash
huggingface-cli repo create rag-chatbot-api --type space --space_sdk docker
```

- [ ] T015 Note your Space URL: `https://huggingface.co/spaces/{USERNAME}/rag-chatbot-api`

- [ ] T016 Configure Space secrets via HF web interface:
  1. Go to: `https://huggingface.co/spaces/{USERNAME}/rag-chatbot-api/settings`
  2. Scroll to "Repository secrets" section
  3. Add each secret:
     - `QDRANT_URL` = your Qdrant Cloud URL
     - `QDRANT_API_KEY` = your Qdrant API key
     - `DATABASE_URL` = your Neon Postgres connection string
     - `COHERE_API_KEY` = your Cohere API key
     - `GEMINI_API_KEY` = your Gemini API key
     - `BOOK_BASE_URL` = `https://{username}.github.io/{repo}/docs`
     - `CORS_ORIGINS` = `["https://{username}.github.io"]`

**Checkpoint**: HF Space created and secrets configured

---

## Phase 5: Deploy to Hugging Face Spaces

**Purpose**: Push code to HF Space and trigger deployment

### 5.1 Initialize Git for HF Space

- [ ] T017 Navigate to chatbot directory and initialize git for HF:
```bash
cd chatbot
git init
git remote add space https://huggingface.co/spaces/{USERNAME}/rag-chatbot-api
```

### 5.2 Prepare and Push Code

- [ ] T018 Stage all files for deployment:
```bash
git add .
git commit -m "Initial deployment: RAG Chatbot API"
```

- [ ] T019 Push to HF Spaces (this triggers deployment):
```bash
git push space main
```
Note: You may need `git push space main --force` for first push

### 5.3 Monitor Deployment

- [ ] T020 Monitor build logs in HF Spaces web interface:
  - Go to: `https://huggingface.co/spaces/{USERNAME}/rag-chatbot-api`
  - Click on "Logs" tab or "Building" status
  - Wait for build to complete (typically 2-5 minutes)
  - Verify "Running" status appears

**Checkpoint**: Application deployed and running on HF Spaces

---

## Phase 6: Deployment Verification

**Purpose**: Verify deployment is working correctly

### 6.1 Health Check Verification

- [ ] T021 Test root endpoint:
```bash
curl https://{USERNAME}-rag-chatbot-api.hf.space/
```
Expected: `{"message": "RAG Chatbot API is running", "version": "1.0.0"}`

- [ ] T022 Test health endpoint:
```bash
curl https://{USERNAME}-rag-chatbot-api.hf.space/api/health
```
Expected: JSON with service statuses (qdrant, database, etc.)

### 6.2 API Endpoint Verification

- [ ] T023 [P] Test selection mode endpoint:
```bash
curl -X POST "https://{USERNAME}-rag-chatbot-api.hf.space/api/chat/selection" \
  -H "Content-Type: application/json" \
  -d '{"selected_text": "Inverse kinematics is the mathematical process of calculating joint angles.", "question": "What is this about?"}'
```
Expected: Response explaining the selected text

- [ ] T024 [P] Test retrieval mode endpoint (requires Cohere API quota):
```bash
curl -X POST "https://{USERNAME}-rag-chatbot-api.hf.space/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is physical AI?", "session_id": "test-session-123"}'
```
Expected: Response with book content and citations

- [ ] T025 [P] Test streaming endpoint:
```bash
curl -N -X POST "https://{USERNAME}-rag-chatbot-api.hf.space/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Hello", "session_id": "test-stream-123"}'
```
Expected: SSE stream with `data:` prefixed chunks

### 6.3 CORS Verification

- [ ] T026 Test CORS headers from allowed origin:
```bash
curl -X OPTIONS "https://{USERNAME}-rag-chatbot-api.hf.space/api/chat" \
  -H "Origin: https://{username}.github.io" \
  -H "Access-Control-Request-Method: POST" \
  -v
```
Expected: `Access-Control-Allow-Origin` header in response

### 6.4 Rate Limiting Verification

- [ ] T027 [P] Test rate limiting is active (make multiple rapid requests):
```bash
for i in {1..35}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST "https://{USERNAME}-rag-chatbot-api.hf.space/api/chat/selection" \
    -H "Content-Type: application/json" \
    -d '{"selected_text": "test", "question": "test"}'
done
```
Expected: Eventually see `429` status codes (rate limited)

**Checkpoint**: All API endpoints verified working

---

## Phase 7: Frontend Integration Update

**Purpose**: Update frontend to use deployed backend

- [ ] T028 Update `physical-ai-robotics-book/src/components/ChatWidget/ChatWidget.jsx`:
  - Change API base URL from `http://localhost:8001` to `https://{USERNAME}-rag-chatbot-api.hf.space`
  - Keep localhost as fallback for development

- [ ] T029 [P] Update `physical-ai-robotics-book/docusaurus.config.ts` if needed:
  - Add any custom configuration for production

- [ ] T030 Build and test frontend locally:
```bash
cd physical-ai-robotics-book
npm run build
npm run serve
```
  - Open browser and test chatbot connects to HF Spaces backend

- [ ] T031 Deploy frontend to GitHub Pages:
```bash
npm run deploy
```

**Checkpoint**: Frontend integrated with deployed backend

---

## Phase 8: Post-Deployment Validation

**Purpose**: Complete end-to-end validation

### 8.1 End-to-End Testing

- [ ] T032 Open production book URL in browser: `https://{username}.github.io/{repo}/docs`
- [ ] T033 Test ChatWidget appears in bottom-right corner
- [ ] T034 Test collapse/expand toggle works
- [ ] T035 [P] Test selection mode:
  - Highlight text on any page
  - Ask a question about the selected text
  - Verify response addresses selected text
- [ ] T036 [P] Test retrieval mode (if Cohere quota available):
  - Clear any text selection
  - Ask a question about the book
  - Verify response includes citations

### 8.2 Error Handling Verification

- [ ] T037 [P] Verify rate limit error displays user-friendly message
- [ ] T038 [P] Verify network error displays appropriate message
- [ ] T039 Verify ChatWidget handles backend unavailability gracefully

### 8.3 Mobile Testing

- [ ] T040 Test on mobile device or mobile browser emulator:
  - ChatWidget is visible and usable
  - Messages display correctly
  - Input field is accessible

**Checkpoint**: Full end-to-end deployment verified

---

## Phase 9: Documentation & Cleanup

**Purpose**: Document deployment and clean up

- [ ] T041 [P] Update `chatbot/README.md` with:
  - Production API URL
  - Example curl commands
  - Rate limits documentation

- [ ] T042 [P] Create `DEPLOYMENT_NOTES.md` with:
  - HF Space URL
  - Date of deployment
  - Any issues encountered and resolutions

- [ ] T043 Commit and push all changes to main repository:
```bash
git add .
git commit -m "feat(deploy): deploy RAG chatbot backend to Hugging Face Spaces"
git push origin 001-rag-chatbot
```

- [ ] T044 Update PR description with deployment status and URLs

**Checkpoint**: Deployment documented and code committed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Pre-Deployment Setup)**: No dependencies - start here
- **Phase 2 (Configuration Files)**: Depends on Phase 1 (need HF account)
- **Phase 3 (Code Updates)**: Can run in parallel with Phase 2
- **Phase 4 (Create HF Space)**: Depends on Phases 1, 2, 3
- **Phase 5 (Deploy)**: Depends on Phase 4
- **Phase 6 (Verification)**: Depends on Phase 5
- **Phase 7 (Frontend Integration)**: Depends on Phase 6 (need working backend URL)
- **Phase 8 (E2E Validation)**: Depends on Phase 7
- **Phase 9 (Documentation)**: Depends on Phase 8

### Parallel Opportunities

Tasks marked [P] can run in parallel within their phase:
- T002, T003: Verify keys while installing CLI
- T012, T013: Health check and debug removal
- T023, T024, T025: Different endpoint tests
- T035, T036: Selection and retrieval mode tests
- T037, T038: Error handling tests
- T041, T042: Documentation updates

---

## Troubleshooting Guide

### Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` for version conflicts |
| App doesn't start | Verify Dockerfile CMD path is correct |
| Secrets not working | Ensure secrets are added to Space settings, not as variables |
| CORS errors | Verify `CORS_ORIGINS` includes exact frontend URL |
| 429 errors | Rate limit reached - wait or adjust limits |
| Streaming not working | Check `Accept: text/event-stream` header |
| Cold start slow | First request after inactivity may take 30-60s |

### Rollback Steps

If deployment has critical issues:
1. Identify last working commit
2. `git revert` to that commit
3. `git push space main --force`
4. Monitor rebuild in HF Spaces

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 44 |
| Phase 1 (Setup) | 5 tasks |
| Phase 2 (Config) | 4 tasks |
| Phase 3 (Code) | 4 tasks |
| Phase 4 (Create Space) | 3 tasks |
| Phase 5 (Deploy) | 4 tasks |
| Phase 6 (Verify) | 7 tasks |
| Phase 7 (Frontend) | 4 tasks |
| Phase 8 (E2E) | 9 tasks |
| Phase 9 (Docs) | 4 tasks |
| Parallel Opportunities | 15 tasks |

**Estimated Time**: 1-2 hours for experienced user, 2-4 hours for first-time HF Spaces deployment
