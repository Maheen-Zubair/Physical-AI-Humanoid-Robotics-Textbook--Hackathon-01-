# Hugging Face Spaces Deployment Procedures

## Deployment Steps

### 1. Prepare Repository
```bash
# Ensure all code is committed
git add .
git commit -m "Prepare for Hugging Face Spaces deployment"
git push origin main
```

### 2. Create Hugging Face Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in details:
   - **Name**: `rag-chatbot-book`
   - **Type**: Docker
   - **SDK**: Leave as default
   - **Hardware**: CPU Basic (for initial deployment)
   - **Visibility**: Public (or Private as needed)

### 3. Configure Environment Variables
In the Space settings, add the following secrets:

| Key | Description | Example |
|-----|-------------|---------|
| `QDRANT_URL` | Qdrant Cloud URL | `https://your-cluster.europe-west1.gcp.cloud.qdrant.io:6333` |
| `QDRANT_API_KEY` | Qdrant API key | `your-actual-api-key` |
| `GEMINI_API_KEY` | Google AI API key | `your-actual-api-key` |
| `DATABASE_URL` | Neon Postgres connection string | `postgresql://user:pass@ep-...us-east-1.aws.neon.tech/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `QDRANT_COLLECTION_NAME` | Qdrant collection name | `book_chunks` |

### 4. Create Required Files for Hugging Face

#### Create app.py for Hugging Face interface:
```python
# app.py
import os
from gradio import components
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.app.main import app as fastapi_app
from chatbot.app.routers import chat, health

# The FastAPI app is already created in main.py
# Hugging Face will run this automatically

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 7860)),
        reload=False
    )
```

#### Create Dockerfile for Hugging Face Spaces:
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY chatbot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose the port
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "chatbot.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

#### Create requirements.txt with all dependencies:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
qdrant-client==1.9.1
asyncpg==0.29.0
google-generativeai==0.4.1
openai==1.6.1
pydantic==2.5.0
python-dotenv==1.0.0
pydantic-settings==2.1.0
slowapi==0.1.9
aiofiles==23.2.1
requests==2.31.0
numpy==1.24.3
tiktoken==0.5.2
```

### 5. Push Deployment Files
```bash
# Add the new files to the repository
git add Dockerfile app.py requirements.txt
git commit -m "Add Hugging Face Spaces deployment files"
git push origin main
```

### 6. Monitor Deployment
1. Check Space logs in Hugging Face UI
2. Wait for build to complete
3. Verify application starts without errors

## Verification Procedures

### 1. Health Check
- **Endpoint**: `GET /api/health`
- **Expected Response**: `{"status": "healthy", "timestamp": "..."}`

### 2. Chat Functionality Test
- **Endpoint**: `POST /api/chat`
- **Test Payload**:
```json
{
  "query": "What is this book about?",
  "context_selection": null,
  "session_id": null
}
```
- **Expected Response**: Valid response with sources

### 3. Selection Mode Test
- **Endpoint**: `POST /api/chat`
- **Test Payload**:
```json
{
  "query": "Explain this concept",
  "context_selection": "This is selected text that should be used for the response",
  "session_id": null
}
```
- **Expected Response**: Response based only on selected text

### 4. Out-of-Scope Detection Test
- **Endpoint**: `POST /api/chat`
- **Test Payload**:
```json
{
  "query": "What is the weather today?",
  "context_selection": null,
  "session_id": null
}
```
- **Expected Response**: Out-of-scope message

### 5. Rate Limiting Test
- Make more than 30 requests per minute from same IP
- **Expected Response**: 429 status code with retry information

### 6. Caching Verification
- Make identical requests
- **Expected Behavior**: Second request should return cached response faster

## Post-Deployment Checklist

### Functionality Verification
- [ ] Health endpoint returns 200
- [ ] Chat endpoint responds to basic queries
- [ ] Selection mode respects Selected Text Rule
- [ ] Out-of-scope questions are detected
- [ ] Citations are properly formatted
- [ ] Rate limiting works as expected
- [ ] Response caching reduces latency for repeated queries

### Performance Verification
- [ ] Response times under 5 seconds for most queries
- [ ] No timeout errors during normal usage
- [ ] Caching improves performance for repeated queries
- [ ] System handles concurrent requests appropriately

### Security Verification
- [ ] Environment variables not exposed in logs
- [ ] Rate limiting prevents abuse
- [ ] No sensitive information in error messages
- [ ] CORS headers properly configured

### Reliability Verification
- [ ] Graceful degradation when services unavailable
- [ ] Error handling provides useful feedback
- [ ] System recovers from partial service failures
- [ ] Logging provides adequate operational visibility

## Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile and requirements.txt for compatibility
2. **App doesn't start**: Verify environment variables are correctly set as secrets
3. **Connection errors**: Ensure service URLs and credentials are correct
4. **Timeout errors**: Check if external services (Qdrant, Gemini) are accessible
5. **Memory issues**: Monitor resource usage and consider upgrading hardware

### Debugging Steps

1. Check Space logs for error messages
2. Verify all environment variables are set as secrets (not regular variables)
3. Test external service connectivity separately
4. Check rate limits and usage quotas for external services
5. Verify Qdrant collection exists and is accessible

## Rollback Procedures

If deployment issues occur:

1. Identify the last known working commit
2. Create a temporary fix branch if needed
3. Revert to stable version and redeploy
4. Monitor logs after rollback
5. Document the issue for future prevention

## Maintenance Procedures

### Regular Maintenance
- Monitor space usage and resource consumption
- Check external service usage quotas
- Review logs for recurring issues
- Update dependencies periodically
- Test backup and recovery procedures

### Scaling Considerations
- Monitor response times during peak usage
- Consider upgrading hardware if needed
- Implement additional caching if beneficial
- Review and adjust rate limits as needed
- Plan for increased usage if popularity grows

## Success Criteria

The deployment is considered successful when:
- [ ] All acceptance tests pass
- [ ] Response times are acceptable (under 5 seconds)
- [ ] All features work as expected
- [ ] Rate limiting functions properly
- [ ] Caching provides performance benefits
- [ ] Error handling is graceful
- [ ] System is stable under normal load