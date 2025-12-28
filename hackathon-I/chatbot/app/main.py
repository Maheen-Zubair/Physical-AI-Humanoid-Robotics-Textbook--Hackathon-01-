from dotenv import load_dotenv
load_dotenv()  # Load .env file before other imports

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import get_settings
from .routers import health, chat
from .middleware.rate_limiter import rate_limiter
import logging


# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot for AI-native book",
    version="1.0.0"
)

# Add CORS middleware with streaming support
# Note: For development, we allow localhost origins explicitly
cors_origins = settings.cors_origins.copy() if isinstance(settings.cors_origins, list) else list(settings.cors_origins)

# Ensure localhost is always allowed in development
dev_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
for origin in dev_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    # Expose headers needed for streaming SSE
    expose_headers=[
        "Content-Type",
        "Cache-Control",
        "Connection",
        "X-Accel-Buffering",
        "Retry-After",
    ],
)

# Add rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting per IP address.
    Skips OPTIONS requests to allow CORS preflight.
    """
    # Skip rate limiting for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    # Get client IP address
    client_ip = request.client.host

    # Check rate limit
    is_allowed, error_msg, retry_after = rate_limiter.check_rate_limit(client_ip)

    if not is_allowed:
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            status_code=429,
            content={"error": error_msg or "Rate limit exceeded", "error_code": "RATE_LIMIT"},
        )

        # Add Retry-After header if available
        if retry_after is not None:
            response.headers["Retry-After"] = str(retry_after)

        return response

    response = await call_next(request)
    return response

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize services on application startup.
    """
    from .services.database import db_connection
    from .services.vector_store import vector_store

    # Validate environment variables
    try:
        _ = get_settings()
        logger.info("Environment variables validated successfully")
    except EnvironmentError as e:
        logger.error(f"Environment validation failed: {e}")
        raise

    # Initialize database connection
    await db_connection.initialize()
    logger.info("Database connection initialized")

    # Initialize vector store
    vector_store.initialize()
    logger.info("Vector store initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up services on application shutdown.
    """
    from .services.database import db_connection

    # Close database connection
    await db_connection.close()
    logger.info("Database connection closed")


@app.get("/")
def read_root():
    """
    Root endpoint for basic health check.
    """
    return {"message": "RAG Chatbot API is running", "version": "1.0.0"}