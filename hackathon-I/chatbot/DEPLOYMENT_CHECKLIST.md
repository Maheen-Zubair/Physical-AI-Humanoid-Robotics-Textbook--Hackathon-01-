# Hugging Face Spaces Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All features implemented and tested locally
- [ ] All unit and integration tests pass
- [ ] Code is committed and pushed to repository
- [ ] `.gitignore` properly excludes unnecessary files
- [ ] Requirements file (`requirements.txt`) is up-to-date
- [ ] Environment variables are referenced correctly in code

### 2. Security Review
- [ ] No hardcoded credentials or secrets in code
- [ ] All sensitive data is accessed via environment variables
- [ ] CORS settings are configured appropriately for production
- [ ] Rate limiting is properly configured
- [ ] Input validation is implemented for all endpoints

### 3. Performance & Reliability
- [ ] Graceful degradation implemented for external services
- [ ] Error handling covers all major failure scenarios
- [ ] Logging is implemented with appropriate detail
- [ ] Rate limits are set appropriately (30/min, 500/day)
- [ ] Database connections are properly managed with connection pooling

## Hugging Face Spaces Setup

### 4. Space Creation
- [ ] Create new Space on Hugging Face Hub
- [ ] Select "Docker" SDK type for custom dependencies
- [ ] Choose appropriate hardware (CPU recommended for RAG chatbot)
- [ ] Set Space visibility (public/private as needed)

### 5. Environment Variables Configuration
- [ ] Add `QDRANT_URL` to Space secrets
- [ ] Add `QDRANT_API_KEY` to Space secrets
- [ ] Add `GEMINI_API_KEY` to Space secrets
- [ ] Add `DATABASE_URL` (Neon Postgres) to Space secrets
- [ ] Add `OPENAI_API_KEY` to Space secrets
- [ ] Add `QDRANT_COLLECTION_NAME` to Space secrets
- [ ] Verify all secrets are properly configured and accessible

### 6. Configuration Files
- [ ] Create `Dockerfile` in root directory
- [ ] Create `app.py` with proper Hugging Face interface (if needed)
- [ ] Create `.hf.space` configuration if using specific Space features
- [ ] Verify `requirements.txt` includes all necessary dependencies

## Docker Configuration

### 7. Dockerfile Setup
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

### 8. App Configuration
- [ ] Ensure application runs on port 7860 (Hugging Face default)
- [ ] Use `os.environ.get()` for all environment variables
- [ ] Handle case where environment variables are missing
- [ ] Implement proper logging to console for monitoring

## Testing & Validation

### 9. Pre-Deployment Testing
- [ ] Test locally with production-like environment variables
- [ ] Verify all API endpoints work as expected
- [ ] Test rate limiting functionality
- [ ] Test error handling and graceful degradation
- [ ] Validate citation formatting works correctly
- [ ] Test Selected Text Rule functionality

### 10. Deployment Process
- [ ] Push all changes to main branch
- [ ] Trigger Space rebuild from Hugging Face UI
- [ ] Monitor build logs for errors
- [ ] Wait for deployment to complete
- [ ] Verify application is running (check Space logs)

## Post-Deployment Validation

### 11. Health Checks
- [ ] Verify health endpoint returns 200 status
- [ ] Test chat endpoint with simple query
- [ ] Test ingestion endpoint with sample content
- [ ] Verify rate limiting works properly
- [ ] Test error handling with invalid inputs
- [ ] **[v2]** Verify Cohere API status in health check response

### 12. Functionality Verification
- [ ] Test semantic search with relevant queries
- [ ] Verify citations appear with proper format
- [ ] Test out-of-scope question detection
- [ ] Test Selected Text Rule functionality
- [ ] Verify mobile responsiveness works
- [ ] Test citation links are functional
- [ ] **[v2]** Test streaming endpoint (`/api/chat/stream`)
- [ ] **[v2]** Test selected-text-query endpoint (`/api/selected-text-query`)
- [ ] **[v2]** Verify mode indicator badges appear in frontend
- [ ] **[v2]** Test selection-mode guardrail (should respond with "This information is not present in the selected text" for out-of-context questions)

### 13. Performance & Reliability
- [ ] Verify graceful degradation when services are unavailable
- [ ] Check structured logging works properly
- [ ] Confirm rate limiting returns proper 429 responses
- [ ] Test concurrent user scenarios
- [ ] Monitor resource usage (memory, CPU)

## Monitoring & Maintenance

### 14. Operational Setup
- [ ] Set up monitoring for API endpoints
- [ ] Configure alerts for service unavailability
- [ ] Document how to access Space logs
- [ ] Plan for regular dependency updates
- [ ] Set up backup strategy for data if needed

### 15. Documentation Updates
- [ ] Update deployment documentation with Space URL
- [ ] Document any Space-specific configuration
- [ ] Update API documentation if needed
- [ ] Add Space maintenance procedures to runbook

## Rollback Plan

### 16. Emergency Procedures
- [ ] Document how to rollback to previous version
- [ ] Have backup Space ready if needed
- [ ] Document contact information for service dependencies
- [ ] Have plan for handling API key rotation
- [ ] Document data migration procedures if needed

## Completion

### 17. Final Verification
- [ ] End-to-end testing completed successfully
- [ ] All acceptance criteria met
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated and published
- [ ] Team notified of successful deployment

---

## v2 API Endpoints Reference

### Streaming Endpoint
```bash
# Test streaming with curl
curl -N -X POST https://your-space.hf.space/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"query": "What is inverse kinematics?", "session_id": "test-123"}'
```

### Selected-Text-Query Endpoint
```bash
# Test selected-text-query (selection mode guaranteed)
curl -X POST https://your-space.hf.space/api/selected-text-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain this in simpler terms", "context_selection": "Inverse kinematics is..."}'
```

### Health Check with Cohere Status
```bash
# Check service health including Cohere API
curl https://your-space.hf.space/api/health
# Expected response includes "cohere": {"status": "ok", ...}
```

---

## Common Issues & Troubleshooting

**Build fails**: Check requirements.txt for compatibility with Python 3.9
**App doesn't start**: Verify the CMD in Dockerfile points to correct entry point
**Environment vars not working**: Ensure they're added as secrets, not variables
**High memory usage**: Optimize vector search and implement caching
**Slow responses**: Consider implementing response caching for common queries
**Rate limiting issues**: Adjust limits based on usage patterns
**Streaming not working**: Check CORS headers include exposed headers for SSE
**Selection mode not enforcing guardrail**: Verify SELECTION_MODE_SYSTEM_PROMPT is active

---

## Rollback Steps

1. If current deployment has critical issues:
   - Identify the last known working commit
   - Revert to that commit and push
   - Trigger Space rebuild from the working version
   - Verify functionality with basic health checks