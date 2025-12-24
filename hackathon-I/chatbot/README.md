# RAG Chatbot for AI-native Book

A Retrieval-Augmented Generation (RAG) chatbot that enables students to ask questions about book content and receive accurate answers with proper citations. The system uses semantic search to find relevant content and provides citations in the format [Source: Chapter Name](URL).

## Features

- **Semantic Search**: Uses vector embeddings to find relevant content from the book
- **Selected Text Rule**: When user selects text, responds using ONLY that text (no vector search)
- **Citation Support**: All responses include proper citations in [Source: Chapter Name](URL) format
- **Out-of-Scope Detection**: Identifies and handles questions outside book scope
- **Mobile Responsive**: Works on all device sizes with responsive design
- **Rate Limiting**: IP-based rate limiting (30/min, 500/day)
- **Graceful Degradation**: Continues to function when individual services are unavailable

## Architecture

The system uses a dual-store pattern:
- **Qdrant Cloud**: Vector store for semantic search
- **Neon Postgres**: Metadata store for chunk content and citations
- **Gemini 2.5 Flash**: For both embeddings and response generation (single API key)

## Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Qdrant Cloud account (free tier)
- Cohere API key (for embeddings using embed-english-v3.0)
- Google AI API key (for response generation with Gemini 2.5 Flash)
- Neon Postgres account (free tier)

## Setup Instructions

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hackathon-I/chatbot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the `chatbot` directory with the following:
   ```env
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=your_neon_postgres_url
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_COLLECTION_NAME=book_chunks
   CORS_ORIGINS=["*"]  # Adjust for production
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd chatbot/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

## API Endpoints

### Chat Endpoint
```
POST /api/chat
```

Request body:
```json
{
  "message": "Your question here",
  "context_selection": "Optional selected text from the book",
  "session_id": "Optional session ID for conversation history"
}
```

Response:
```json
{
  "response": "Answer to your question",
  "citations": [
    {
      "chapter": "Chapter Name",
      "url": "https://source-url.com",
      "section": "Section Title"
    }
  ],
  "sources_used": ["chunk_id_1", "chunk_id_2"]
}
```

### Health Check
```
GET /api/health
```

### Ingestion Endpoint
```
POST /api/ingest
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `QDRANT_URL` | Qdrant Cloud URL | Yes |
| `QDRANT_API_KEY` | Qdrant API key | Yes |
| `COHERE_API_KEY` | Cohere API key for embeddings | Yes |
| `GEMINI_API_KEY` | Google AI API key for response generation | Yes |
| `DATABASE_URL` | Neon Postgres connection string | Yes |
| `QDRANT_COLLECTION_NAME` | Qdrant collection name | Yes |
| `CORS_ORIGINS` | Allowed origins (JSON array) | No (defaults to ["*"]) |

## Development

### Running Tests
```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend && npm test
```

### Code Formatting
```bash
# Backend formatting
black app/
flake8 app/

# Frontend formatting
cd frontend && npm run format
```

## Deployment

### Hugging Face Spaces Deployment

1. Create a new Space on Hugging Face
2. Add your environment variables in the Space settings
3. Use the following `Dockerfile` or `app.py` approach for deployment
4. Ensure all dependencies are in `requirements.txt`

### Configuration for Production

- Update CORS origins to specific domains
- Increase rate limits if needed
- Set up proper logging and monitoring
- Enable HTTPS

## Error Handling

The system implements graceful degradation:

- If Qdrant is unavailable, returns empty search results
- If Neon is unavailable, returns partial results without content
- If Gemini API is unavailable, uses fallback responses
- All errors are logged with structured logging

## Rate Limiting

- 30 requests per minute per IP address
- 500 requests per day per IP address
- Returns 429 status code with retry information when limits are exceeded

## Out-of-Scope Detection

Questions with similarity scores below 0.65 are considered out-of-scope and receive appropriate responses indicating the question is outside the book's content.

## Selected Text Rule

When `context_selection` is provided in the request, the system:
1. Ignores vector search completely
2. Responds using only the provided selected text
3. Still provides citations based on the selected content

## Troubleshooting

### Common Issues

1. **Qdrant Connection Errors**: Verify your QDRANT_URL and QDRANT_API_KEY are correct
2. **Embedding Issues**: Check your GEMINI_API_KEY and ensure it has proper permissions
3. **Database Connection**: Verify your DATABASE_URL is properly formatted
4. **Rate Limiting**: Check if you're exceeding the configured limits

### Logs

Check application logs for detailed error information. The system uses structured logging for all error scenarios.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For support, please open an issue in the repository or contact [support information].