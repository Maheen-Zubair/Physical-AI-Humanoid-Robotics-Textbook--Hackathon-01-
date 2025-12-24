from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import time
import asyncio
from ..services.database import db_connection
from ..services.vector_store import vector_store
from ..services.embedding_service import embedding_service
from ..config import get_settings


router = APIRouter()


class HealthStatus(BaseModel):
    """
    Model representing the health status of the application.
    """
    status: str
    timestamp: datetime
    services: Dict[str, Any]
    details: Optional[Dict[str, Any]] = None


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint to verify the application and its dependencies are running properly.
    """
    start_time = time.time()
    services_status = {}
    overall_status = "healthy"

    # Check if environment variables are properly loaded
    try:
        settings = get_settings()
        services_status["environment"] = {"status": "ok", "message": "Environment variables loaded"}
    except Exception as e:
        services_status["environment"] = {"status": "error", "message": str(e)}
        overall_status = "unhealthy"

    # Check database connectivity
    try:
        async with db_connection.get_connection() as conn:
            await conn.fetchval("SELECT 1")
        services_status["database"] = {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        services_status["database"] = {"status": "error", "message": str(e)}
        overall_status = "unhealthy"

    # Check Qdrant connectivity
    try:
        client = vector_store.client
        # Try to get collection info as a simple connectivity test
        client.get_collection("book_embeddings")
        services_status["vector_store"] = {"status": "ok", "message": "Qdrant connection successful"}
    except Exception as e:
        services_status["vector_store"] = {"status": "error", "message": str(e)}
        overall_status = "unhealthy"

    # Check Cohere API connectivity
    try:
        cohere_ok = await embedding_service.ping()
        if cohere_ok:
            services_status["cohere"] = {"status": "ok", "message": "Cohere API responding"}
        else:
            services_status["cohere"] = {"status": "degraded", "message": "Cohere API not responding"}
            overall_status = "degraded"
    except Exception as e:
        services_status["cohere"] = {"status": "error", "message": str(e)}
        overall_status = "unhealthy"

    # Check external API keys (quick verification)
    try:
        if not settings.cohere_api_key or not settings.gemini_api_key:
            raise Exception("Missing API keys")
        services_status["api_keys"] = {"status": "ok", "message": "Cohere and Gemini API keys present"}
    except Exception as e:
        services_status["api_keys"] = {"status": "error", "message": str(e)}
        overall_status = "unhealthy"

    response_time = time.time() - start_time

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services_status,
        details={"response_time": f"{response_time:.3f}s"}
    )