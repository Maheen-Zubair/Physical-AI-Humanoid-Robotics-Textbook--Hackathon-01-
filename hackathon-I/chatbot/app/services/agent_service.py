from google import genai
from google.genai import types, errors
from typing import Dict, Any, List, AsyncGenerator, Optional
from ..config import get_settings
from ..models.query_context import QueryContext
from ..models.source import Source
import logging
import re
import asyncio


logger = logging.getLogger(__name__)


# CRITICAL: Hard guardrail for selection mode - forbids external knowledge
SELECTION_MODE_SYSTEM_PROMPT = """You are a helpful assistant explaining ONLY the user-selected text.

ABSOLUTE RULES (MUST FOLLOW):
1. You can ONLY use information from the selected text provided below.
2. You MUST NOT use any external knowledge, prior training, or information from other sources.
3. If the answer is not present in the selected text, you MUST respond EXACTLY with:
   "This information is not present in the selected text."
4. Do NOT guess, infer beyond what's written, or add context from outside the selection.
5. Do NOT cite any external sources - you are ONLY explaining the user's selection.
6. Keep explanations clear and focused on what is LITERALLY in the selected text.

IMPORTANT: If asked about something that cannot be directly answered from the selected text,
respond with: "This information is not present in the selected text."
"""

# System prompt for retrieval mode
RETRIEVAL_MODE_SYSTEM_PROMPT = """You are a helpful assistant for readers of the Physical AI & Humanoid Robotics textbook.

RULES:
1. Answer ONLY using the provided context from the book
2. If context is insufficient, say "I couldn't find information about that in the book"
3. Include citations in format: [Source: {title}]({url})
4. Keep responses concise and educational
5. If asked about topics not in context, politely decline
6. Be honest about uncertainty - if you can't answer based on the context, say so clearly
"""


class AgentService:
    """
    Service to handle response generation using Gemini 2.5 Flash.
    Supports both streaming and non-streaming modes with automatic fallback.
    """

    # Streaming configuration
    STREAMING_TIMEOUT_SECONDS = 30
    MAX_STREAMING_RETRIES = 2

    def __init__(self):
        """
        Initialize the agent service with API configuration.
        """
        settings = get_settings()
        # Using new google-genai SDK
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = 'gemini-2.5-flash'
        self.settings = settings

    def _get_system_prompt(self, mode: str) -> str:
        """
        Get the appropriate system prompt based on the context mode.

        CRITICAL: Selection mode uses a hard guardrail that forbids external knowledge.

        Args:
            mode: Either 'selection' or 'retrieval'

        Returns:
            The appropriate system prompt
        """
        if mode == "selection":
            return SELECTION_MODE_SYSTEM_PROMPT
        else:
            return RETRIEVAL_MODE_SYSTEM_PROMPT

    def format_context_for_prompt(self, context: QueryContext) -> str:
        """
        Format the query context into a prompt format for the LLM.

        Args:
            context: The query context containing chunks and query

        Returns:
            Formatted context string
        """
        if context.mode == "selection":
            # For selection mode, only use the selected text with clear boundaries
            selected_chunk = context.chunks[0] if context.chunks else None
            if selected_chunk:
                return f"""
SELECTED TEXT (this is the ONLY information you may use):
---
{selected_chunk.content}
---

User's question about this selection: {context.query}
"""
            else:
                return f"No text was selected. Question: {context.query}"
        else:
            # For retrieval mode, format the retrieved chunks
            formatted_chunks = []
            for chunk in context.chunks:
                if chunk.source_url:
                    formatted_chunks.append(
                        f'<context source="{chunk.chapter_title}" section="{chunk.section_title}" url="{chunk.source_url}">\n{chunk.content}\n</context>'
                    )
                else:
                    formatted_chunks.append(
                        f'<context source="{chunk.chapter_title}" section="{chunk.section_title}">\n{chunk.content}\n</context>'
                    )

            context_text = "\n\n".join(formatted_chunks)
            return f"CONTEXT FROM BOOK:\n\n{context_text}\n\nQuestion: {context.query}"

    def extract_citations_from_response(self, response: str) -> List[Source]:
        """
        Extract citations from the response in the format [Source: Chapter Name](URL).

        Args:
            response: The response text from the LLM

        Returns:
            List of Source objects extracted from citations
        """
        # Pattern to match [Source: Title](URL) format
        citation_pattern = r'\[Source:\s*([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(citation_pattern, response)

        sources = []
        for title, url in matches:
            sources.append(Source(title=title.strip(), url=url.strip()))

        return sources

    def is_out_of_scope_response(self, response_text: str) -> bool:
        """
        Determine if the response indicates the question was out of scope.

        Args:
            response_text: The response text from the LLM

        Returns:
            True if the response indicates out-of-scope, False otherwise
        """
        out_of_scope_indicators = [
            "couldn't find information about that in the book",
            "not mentioned in the provided context",
            "not covered in the provided text",
            "no information provided about",
            "not found in the context",
            "not in the book",
            "out of scope",
            "not discussed",
            "not addressed"
        ]

        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in out_of_scope_indicators)

    async def generate_response(self, context: QueryContext) -> Dict[str, Any]:
        """
        Generate a response based on the provided context using Gemini.

        Args:
            context: The query context containing chunks and query

        Returns:
            Dictionary containing the response and sources
        """
        try:
            # Format the context for the prompt
            formatted_context = self.format_context_for_prompt(context)

            # Get the appropriate system prompt based on mode
            # CRITICAL: Selection mode uses hard guardrail that forbids external knowledge
            system_prompt = self._get_system_prompt(context.mode)

            # Combine system prompt with formatted context
            full_prompt = f"{system_prompt}\n\n{formatted_context}"

            # Generate content using Gemini with new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )

            # Get the text response
            response_text = response.text

            # Extract citations from the response
            sources = self.extract_citations_from_response(response_text)

            # If no citations were found in retrieval mode, add fallback citations
            if context.mode == "retrieval" and not sources and context.chunks:
                # Add a fallback citation from the first chunk
                first_chunk = context.chunks[0]
                if first_chunk.source_url:
                    fallback_citation = f" [Source: {first_chunk.chapter_title}]({first_chunk.source_url})"
                    response_text += fallback_citation
                    sources.append(Source(title=first_chunk.chapter_title, url=first_chunk.source_url))

            return {
                "response": response_text,
                "sources": sources,
                "is_out_of_scope": self.is_out_of_scope_response(response_text),
                "mode": context.mode
            }

        except errors.APIError as e:
            logger.error(f"Gemini API error (code={e.code}): {e.message}")
            return {
                "response": "I encountered an error while processing your request. Please try again.",
                "sources": [],
                "is_out_of_scope": False,
                "mode": context.mode
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I encountered an error while processing your request. Please try again.",
                "sources": [],
                "is_out_of_scope": False,
                "mode": context.mode
            }

    async def generate_response_stream(
        self,
        context: QueryContext
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using Gemini 2.5 Flash.
        Automatically falls back to non-streaming if streaming fails.

        Args:
            context: The query context containing chunks and query

        Yields:
            Text chunks as they become available
        """
        formatted_context = self.format_context_for_prompt(context)
        system_prompt = self._get_system_prompt(context.mode)
        full_prompt = f"{system_prompt}\n\n{formatted_context}"

        try:
            logger.info(f"Starting streaming response (mode={context.mode})")

            # Use synchronous streaming generator with async wrapper
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )

            chunk_count = 0
            for chunk in response_stream:
                if chunk.text:
                    chunk_count += 1
                    yield chunk.text

            logger.info(f"Streaming complete: {chunk_count} chunks delivered")

        except errors.APIError as e:
            logger.error(f"Gemini streaming API error (code={e.code}): {e.message}")
            logger.warning("Falling back to non-streaming response")
            yield await self._fallback_to_non_streaming(context)

        except asyncio.TimeoutError:
            logger.error(f"Streaming timeout after {self.STREAMING_TIMEOUT_SECONDS}s")
            logger.warning("Falling back to non-streaming response due to timeout")
            yield await self._fallback_to_non_streaming(context)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            logger.warning("Falling back to non-streaming response due to error")
            yield await self._fallback_to_non_streaming(context)

    async def _fallback_to_non_streaming(self, context: QueryContext) -> str:
        """
        Fallback to non-streaming generation when streaming fails.

        Args:
            context: The query context

        Returns:
            Complete response text
        """
        logger.info("Executing non-streaming fallback")
        try:
            result = await self.generate_response(context)
            return result.get("response", "I encountered an error. Please try again.")
        except Exception as e:
            logger.error(f"Non-streaming fallback also failed: {e}")
            return "I encountered an error processing your request. Please try again later."


# Global instance
agent_service = AgentService()