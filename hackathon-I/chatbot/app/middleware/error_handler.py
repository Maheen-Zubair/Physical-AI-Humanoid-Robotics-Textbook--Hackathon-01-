from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable, Awaitable
import logging
import traceback
from datetime import datetime


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Centralized error handling middleware for all exception types.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        Dispatch method to intercept and handle exceptions.
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Handle FastAPI HTTPExceptions
            return await self.handle_http_exception(request, e)
        except StarletteHTTPException as e:
            # Handle Starlette HTTPExceptions
            return await self.handle_starlette_http_exception(request, e)
        except Exception as e:
            # Handle all other exceptions
            return await self.handle_general_exception(request, e)


    async def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle FastAPI HTTPExceptions.
        """
        error_details = {
            "error": str(exc.detail) if hasattr(exc, 'detail') else "Internal Server Error",
            "error_code": getattr(exc, 'error_code', 'INTERNAL_ERROR'),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method
        }

        # Structured logging for the error
        logger.error(
            "HTTP Exception occurred",
            extra={
                "error_type": "HTTPException",
                "error_code": exc.status_code,
                "request_url": str(request.url),
                "request_method": request.method,
                "error_detail": str(exc.detail),
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_details
        )


    async def handle_starlette_http_exception(self, request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle Starlette HTTPExceptions.
        """
        error_details = {
            "error": str(exc.detail) if hasattr(exc, 'detail') else "Internal Server Error",
            "error_code": getattr(exc, 'error_code', 'INTERNAL_ERROR'),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method
        }

        # Structured logging for the error
        logger.error(
            "Starlette HTTP Exception occurred",
            extra={
                "error_type": "StarletteHTTPException",
                "error_code": exc.status_code,
                "request_url": str(request.url),
                "request_method": request.method,
                "error_detail": str(exc.detail),
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_details
        )


    async def handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle all other exceptions.
        """
        # Log the full traceback
        logger.error(f"Unhandled Exception: {str(exc)}", extra={
            "request_url": str(request.url),
            "request_method": request.method,
            "traceback": traceback.format_exc()
        })

        # Don't expose internal error details to clients
        error_details = {
            "error": "An unexpected error occurred",
            "error_code": "UNEXPECTED_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method
        }

        return JSONResponse(
            status_code=500,
            content=error_details
        )


# Function to register the error handler middleware with the app
def register_error_handler(app):
    """
    Register the error handler middleware with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(ErrorHandlerMiddleware)