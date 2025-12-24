from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime
import logging
import asyncio
import json

from ..models.chat_request import ChatRequest, SelectedTextRequest
from ..models.chat_response import ChatResponse
from ..models.chat_session import ChatMessage, MessageRole
from ..services.router_service import router_service
from ..services.embedding_service import embedding_service
from ..services.search_service import search_service
from ..services.metadata_service import metadata_service
from ..services.context_service import context_service
from ..services.agent_service import agent_service
from ..services.citation_service import citation_service
from ..services.session_service import session_service
from ..services.scope_service import scope_service
from ..services.cache_service import response_cache
from ..exceptions import ChatbotException, RateLimitError, EmbeddingError, LLMError


router = APIRouter()
logger = logging.getLogger(__name__)


def get_user_friendly_error(error: Exception) -> tuple[str, str]:
    """
    Convert an exception to a user-friendly error message and error code.

    Returns:
        Tuple of (user_message, error_code)
    """
    if isinstance(error, ChatbotException):
        return error.user_message, error.error_code.value

    # Fallback for unexpected errors
    error_str = str(error).lower()

    if "rate limit" in error_str or "429" in error_str:
        return (
            "The API rate limit has been reached. Please try selecting text from the book and asking about it instead.",
            "RATE_LIMIT"
        )

    if "timeout" in error_str:
        return "The request timed out. Please try again.", "TIMEOUT"

    if "connection" in error_str:
        return "Unable to connect to the server. Please check your connection.", "CONNECTION_ERROR"

    return "An unexpected error occurred. Please try again.", "UNKNOWN_ERROR"


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint to handle user queries and return responses.
    Supports both retrieval mode (semantic search) and selection mode (user-selected text only).
    """
    try:
        # Log the incoming request
        logger.info(f"Received chat request for session {request.session_id}")

        # Check cache first for identical requests (skip if session_id is provided to maintain conversation context)
        if not request.session_id:  # Only cache non-session requests
            cached_response = await response_cache.get(request.query, request.context_selection)
            if cached_response:
                logger.info(f"Returning cached response for query: {request.query[:50]}...")
                return ChatResponse(**cached_response)

        # Route the request to determine processing mode
        routing_result = router_service.route_request(request)
        mode = routing_result["mode"]

        # Add user message to session if session_id is provided
        if request.session_id:
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=request.query,
                context_mode=mode if mode != "retrieval" else None  # Only set for non-retrieval modes
            )
            session_service.add_message_to_session(request.session_id, user_message)

        # Process based on mode
        if routing_result["process_selection"]:
            # Selection mode: use only the provided context_selection
            logger.info(f"Processing in selection mode for session {request.session_id}")

            # Assemble context with selected text
            query_context = context_service.assemble_selection_context(
                query=request.query,
                selected_text=request.context_selection,
                session_id=request.session_id
            )

            # Generate response using agent service
            response_data = await agent_service.generate_response(query_context)

            # Validate and process citations
            processed_response, citation_valid = citation_service.validate_citations(
                response_data["response"],
                query_context
            )

            # For selection mode, out-of-scope is less likely since user provides context
            is_out_of_scope = response_data.get("is_out_of_scope", False)
            out_of_scope_reason = "User provided context" if is_out_of_scope else ""

        elif routing_result["perform_search"]:
            # Retrieval mode: perform semantic search
            logger.info(f"Processing in retrieval mode for session {request.session_id}")

            # Generate embedding for the query
            query_embedding = embedding_service.embed_text(request.query)

            # Perform similarity search
            similar_chunks = await search_service.search_similar_chunks_with_content(
                query_embedding=query_embedding,
                limit=5  # Get top 5 similar chunks
            )

            # Assemble context from retrieved chunks
            query_context = context_service.assemble_context(
                query=request.query,
                retrieved_chunks=similar_chunks,
                session_id=request.session_id,
                max_tokens=2000
            )

            # Generate response using agent service
            response_data = await agent_service.generate_response(query_context)

            # Validate and process citations
            processed_response, citation_valid = citation_service.validate_citations(
                response_data["response"],
                query_context
            )

            # Detect out-of-scope using both similarity and LLM analysis
            is_out_of_scope, out_of_scope_reason, confidence = scope_service.detect_out_of_scope(
                chunks=similar_chunks,
                llm_response=response_data["response"],
                llm_indicates_out_of_scope=response_data.get("is_out_of_scope", False)
            )

            # If out of scope, suggest related topics
            if is_out_of_scope:
                related_topics = scope_service.suggest_related_topics(
                    query=request.query,
                    chunks=similar_chunks,
                    max_suggestions=3
                )
                if related_topics:
                    topic_suggestions = f"\n\nYou might find information about: {', '.join(related_topics)}"
                    processed_response += topic_suggestions

        else:
            # This shouldn't happen with proper routing, but handle as retrieval mode
            logger.warning("Unexpected routing result, defaulting to retrieval mode")
            raise HTTPException(status_code=400, detail="Invalid request routing")

        # Add assistant message to session if session_id is provided
        if request.session_id:
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=processed_response
            )
            session_service.add_message_to_session(request.session_id, assistant_message)

        # Create and return the response
        response = ChatResponse(
            response=processed_response,
            sources=response_data["sources"],
            session_id=request.session_id or "",
            timestamp=datetime.utcnow(),
            out_of_scope=is_out_of_scope,
            selection_mode=(mode in ["selection", "selection_truncated"]),
            selection_ignored=(mode == "retrieval" and request.context_selection is not None and not request.context_selection.strip())
        )

        # Cache the response if no session_id is provided (to avoid caching conversation-specific responses)
        if not request.session_id:  # Only cache non-session requests
            cache_response_data = {
                "response": response.response,
                "sources": response.sources,
                "session_id": response.session_id,
                "timestamp": response.timestamp.isoformat() if response.timestamp else None,
                "out_of_scope": response.out_of_scope,
                "selection_mode": response.selection_mode,
                "selection_ignored": response.selection_ignored
            }
            await response_cache.set(request.query, request.context_selection, cache_response_data)
            logger.info(f"Cached response for query: {request.query[:50]}...")

        logger.info(f"Successfully processed chat request for session {request.session_id}")
        return response

    except ChatbotException as e:
        logger.error(f"Chatbot error processing request: {e.error_code.value} - {e}")
        user_message, error_code = e.user_message, e.error_code.value

        # Return a response with the error message instead of raising HTTP exception
        return ChatResponse(
            response=user_message,
            sources=[],
            session_id=request.session_id or "",
            timestamp=datetime.utcnow(),
            out_of_scope=True,
            selection_mode=False,
            selection_ignored=False,
            error_code=error_code
        )
    except Exception as e:
        logger.error(f"Unexpected error processing chat request: {e}")
        user_message, error_code = get_user_friendly_error(e)

        return ChatResponse(
            response=user_message,
            sources=[],
            session_id=request.session_id or "",
            timestamp=datetime.utcnow(),
            out_of_scope=True,
            selection_mode=False,
            selection_ignored=False,
            error_code=error_code
        )


# Additional endpoint to get conversation history
@router.get("/chat/history/{session_id}", response_model=List[ChatMessage])
async def get_conversation_history(session_id: str):
    """
    Get the conversation history for a session.
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return session.messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation history")


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    Returns a streaming response with real-time text chunks.
    """
    logger.info(f"Received streaming chat request for session {request.session_id}")

    async def generate_stream():
        """Generate SSE stream from the agent response."""
        try:
            # Route the request to determine processing mode
            routing_result = router_service.route_request(request)
            mode = routing_result["mode"]

            # Send mode information first
            mode_data = json.dumps({"type": "mode", "mode": mode})
            yield f"data: {mode_data}\n\n"

            if routing_result["process_selection"]:
                # Selection mode: use only the provided context_selection
                logger.info(f"Streaming in selection mode for session {request.session_id}")

                query_context = context_service.assemble_selection_context(
                    query=request.query,
                    selected_text=request.context_selection,
                    session_id=request.session_id
                )
            else:
                # Retrieval mode: perform semantic search
                logger.info(f"Streaming in retrieval mode for session {request.session_id}")

                query_embedding = embedding_service.embed_text(request.query)
                similar_chunks = await search_service.search_similar_chunks_with_content(
                    query_embedding=query_embedding,
                    limit=5
                )

                query_context = context_service.assemble_context(
                    query=request.query,
                    retrieved_chunks=similar_chunks,
                    session_id=request.session_id,
                    max_tokens=2000
                )

            # Stream the response chunks
            full_response = ""
            async for chunk in agent_service.generate_response_stream(query_context):
                full_response += chunk
                chunk_data = json.dumps({"type": "content", "text": chunk})
                yield f"data: {chunk_data}\n\n"

            # Extract sources from the complete response
            sources = agent_service.extract_citations_from_response(full_response)
            sources_data = [{"title": s.title, "url": s.url} for s in sources]

            # Send final metadata
            done_data = json.dumps({
                "type": "done",
                "sources": sources_data,
                "mode": mode,
                "out_of_scope": agent_service.is_out_of_scope_response(full_response)
            })
            yield f"data: {done_data}\n\n"

            # Send SSE done signal
            yield "data: [DONE]\n\n"

            logger.info(f"Streaming complete for session {request.session_id}")

        except ChatbotException as e:
            logger.error(f"Chatbot error in streaming endpoint: {e.error_code.value} - {e}")
            error_data = json.dumps({
                "type": "error",
                "message": e.user_message,
                "error_code": e.error_code.value,
                "recoverable": e.recoverable
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Unexpected error in streaming endpoint: {e}")
            user_message, error_code = get_user_friendly_error(e)
            error_data = json.dumps({
                "type": "error",
                "message": user_message,
                "error_code": error_code,
                "recoverable": True
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/selected-text-query", response_model=ChatResponse)
async def selected_text_query_endpoint(request: SelectedTextRequest):
    """
    Explicit endpoint for selected-text-only queries.
    This endpoint REQUIRES context_selection and NEVER performs vector search.
    Use this when you want to guarantee selection-only mode.
    """
    try:
        logger.info(f"Received selected-text query for session {request.session_id}")

        # Add user message to session if session_id is provided
        if request.session_id:
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=request.query,
                context_mode="selection"
            )
            session_service.add_message_to_session(request.session_id, user_message)

        # Assemble context with ONLY the selected text (no search)
        query_context = context_service.assemble_selection_context(
            query=request.query,
            selected_text=request.context_selection,
            session_id=request.session_id
        )

        # Generate response using agent service with selection mode guardrail
        response_data = await agent_service.generate_response(query_context)

        # Validate and process citations (should be empty for selection mode)
        processed_response, citation_valid = citation_service.validate_citations(
            response_data["response"],
            query_context
        )

        # Add assistant message to session if session_id is provided
        if request.session_id:
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=processed_response
            )
            session_service.add_message_to_session(request.session_id, assistant_message)

        response = ChatResponse(
            response=processed_response,
            sources=[],  # Selection mode never has external sources
            session_id=request.session_id or "",
            timestamp=datetime.utcnow(),
            out_of_scope=response_data.get("is_out_of_scope", False),
            selection_mode=True,
            selection_ignored=False
        )

        logger.info(f"Successfully processed selected-text query for session {request.session_id}")
        return response

    except Exception as e:
        logger.error(f"Error processing selected-text query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")