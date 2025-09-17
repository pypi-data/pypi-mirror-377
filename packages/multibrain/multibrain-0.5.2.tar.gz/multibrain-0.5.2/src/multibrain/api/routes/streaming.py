# src/multibrain/api/routes/streaming.py

import asyncio
import json
import logging
from typing import List, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
import httpx
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["streaming"])


class LLMConfig(BaseModel):
    """Configuration for a single LLM endpoint"""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    model: str
    api_key: str = Field(alias="apiKey")
    enabled: bool = True


class SummaryConfig(BaseModel):
    """Configuration for the summary LLM"""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    model: str
    api_key: str = Field(alias="apiKey")


class StreamQueryRequest(BaseModel):
    """Request model for streaming queries"""

    model_config = ConfigDict(populate_by_name=True)

    query: str
    llm_configs: List[LLMConfig] = Field(alias="llmConfigs")
    summary_config: Optional[SummaryConfig] = Field(None, alias="summaryConfig")
    # Follow-up support
    context: Optional[str] = Field(None, description="Previous conversation context")
    is_follow_up: bool = Field(
        False, alias="isFollowUp", description="Whether this is a follow-up query"
    )
    parent_query_id: Optional[str] = Field(
        None, alias="parentQueryId", description="ID of parent query"
    )


class ValidationRequest(BaseModel):
    """Request model for LLM validation"""

    model_config = ConfigDict(populate_by_name=True)

    url: str
    model: str
    api_key: str = Field(alias="apiKey")


class ModelsRequest(BaseModel):
    """Request model for fetching available models"""

    model_config = ConfigDict(populate_by_name=True)

    url: str
    api_key: str = Field(alias="apiKey")


async def stream_openai_response(
    llm_config: LLMConfig | SummaryConfig,
    query: str,
    client: httpx.AsyncClient,
    context: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream response from an OpenAI-compatible endpoint"""

    logger.info(f"Starting stream from {llm_config.name} ({llm_config.model})")

    headers = {
        "Authorization": f"Bearer {llm_config.api_key}",
        "Content-Type": "application/json",
    }

    # Support different auth header formats
    if "anthropic" in llm_config.url.lower():
        headers["X-API-Key"] = llm_config.api_key
        del headers["Authorization"]

    # Build messages with context if provided
    messages = []
    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Previous conversation summary:\n{context}\n\nPlease consider this context when responding to the follow-up question.",
            }
        )
    messages.append({"role": "user", "content": query})

    payload = {
        "model": llm_config.model,
        "messages": messages,
        "stream": True,
    }

    try:
        async with client.stream(
            "POST",
            f"{llm_config.url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=300.0,
        ) as response:
            response.raise_for_status()
            logger.info(
                f"Got response from {llm_config.name}, status: {response.status_code}"
            )

            chunk_count = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                chunk_count += 1
                                yield content
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse SSE data: {data}")

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code} from {llm_config.name}"
        logger.error(f"{error_msg}: {e.response.text}")
        yield f"\n\n[ERROR: {error_msg}]"
    except Exception as e:
        error_msg = f"Error streaming from {llm_config.name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield f"\n\n[ERROR: {error_msg}]"


async def generate_sse_events(request: StreamQueryRequest):
    """Generate Server-Sent Events for all LLM responses"""

    logger.info(f"Starting SSE stream for query: {request.query[:50]}...")

    async with httpx.AsyncClient() as client:
        # Start streaming from all enabled LLMs
        llm_responses = {}
        response_queues = {}
        tasks = []

        # Send initial events for all enabled LLMs
        for llm_config in request.llm_configs:
            if not llm_config.enabled:
                continue

            event_data = {
                "type": "llm_start",
                "llm_id": llm_config.id,
                "llm_name": llm_config.name,
                "timestamp": datetime.utcnow().isoformat(),
            }
            yield f"data: {json.dumps(event_data)}\n\n"

        # Create async queue for each LLM to stream chunks immediately
        for llm_config in request.llm_configs:
            if llm_config.enabled:
                response_queues[llm_config.id] = asyncio.Queue()

        # Create tasks for streaming from each LLM
        async def stream_llm_wrapper(config: LLMConfig):
            """Stream responses and put chunks in queue immediately"""
            response_text = ""
            queue = response_queues[config.id]

            try:
                async for chunk in stream_openai_response(
                    config, request.query, client, request.context
                ):
                    response_text += chunk
                    # Put chunk event in queue immediately
                    chunk_event = {
                        "type": "llm_chunk",
                        "llm_id": config.id,
                        "content": chunk,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await queue.put(chunk_event)

                # Store complete response for summary
                llm_responses[config.id] = {
                    "name": config.name,
                    "response": response_text,
                }

                # Add completion event
                await queue.put(
                    {
                        "type": "llm_complete",
                        "llm_id": config.id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            except Exception as e:
                # Add error event
                await queue.put(
                    {
                        "type": "llm_error",
                        "llm_id": config.id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            finally:
                # Signal end of stream
                await queue.put(None)

        # Start all LLM streaming tasks
        for llm_config in request.llm_configs:
            if llm_config.enabled:
                task = asyncio.create_task(stream_llm_wrapper(llm_config))
                tasks.append(task)

        # Process events from all queues as they arrive
        active_streams = set(response_queues.keys())

        while active_streams:
            # Check all queues for available events
            for llm_id in list(active_streams):
                queue = response_queues[llm_id]
                try:
                    # Try to get an event without blocking
                    event = queue.get_nowait()
                    if event is None:
                        # Stream ended
                        active_streams.remove(llm_id)
                    else:
                        # Yield the event immediately
                        yield f"data: {json.dumps(event)}\n\n"
                        # Force flush to ensure event is sent
                        await asyncio.sleep(0)
                except asyncio.QueueEmpty:
                    # No event available yet
                    pass

            # Small delay to prevent busy waiting
            if active_streams:
                await asyncio.sleep(0.01)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Generate summary if configured
        if request.summary_config and len(llm_responses) > 0:
            yield f"data: {json.dumps({
                'type': 'summary_start',
                'timestamp': datetime.utcnow().isoformat()
            })}\n\n"

            # Build summary prompt
            if request.is_follow_up and request.context:
                summary_prompt = f"""Task: Generate a concise, accurate summary by cross-referencing the following responses to a follow-up question.
Consider the previous conversation context and ensure continuity.

Previous Context:
{request.context}

Follow-up Query:
{request.query}

New Responses:
"""
            else:
                summary_prompt = f"""Task: Generate a concise, accurate summary by cross-referencing the following responses.
Correct any discrepancies, remove hallucinations, and ensure factual integrity.

Original Query:
{request.query}

Source Responses:
"""

            for llm_id, response_data in llm_responses.items():
                summary_prompt += (
                    f"\n{response_data['name']}:\n{response_data['response']}\n"
                )

            summary_prompt += """
Requirements:
- Prioritize factual consistency between sources
- Resolve conflicting information
- Eliminate redundant or fabricated content
- Ensure the summary reflects only validated information
- Remove hallucinations
- Don't note incorrect information, just omit it
- Don't mention information was removed or discrepancies, just omit it
- Write "Summary:" then write the summary
"""

            # Stream summary response
            async for chunk in stream_openai_response(
                request.summary_config,
                summary_prompt,
                client,
                request.context if request.is_follow_up else None,
            ):
                yield f"data: {json.dumps({
                    'type': 'summary_chunk',
                    'content': chunk,
                    'timestamp': datetime.utcnow().isoformat()
                })}\n\n"

            yield f"data: {json.dumps({
                'type': 'summary_complete',
                'timestamp': datetime.utcnow().isoformat()
            })}\n\n"

        # Send final completion event
        completion_event = {
            "type": "query_complete",
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info("Sending query_complete event")
        yield f"data: {json.dumps(completion_event)}\n\n"


@router.post("/query/stream")
async def stream_query(request: StreamQueryRequest):
    """Stream responses from multiple LLMs using Server-Sent Events"""

    if not request.llm_configs:
        raise HTTPException(status_code=400, detail="No LLM configurations provided")

    enabled_llms = [llm for llm in request.llm_configs if llm.enabled]
    if not enabled_llms:
        raise HTTPException(status_code=400, detail="No enabled LLMs found")

    return StreamingResponse(
        generate_sse_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Transfer-Encoding": "chunked",
        },
    )


# Alias for frontend compatibility
@router.post("/stream")
async def stream_query_alias(request: StreamQueryRequest):
    """Alias for /api/query/stream to match frontend expectations"""
    return await stream_query(request)


@router.post("/llm/validate")
async def validate_llm(request: ValidationRequest):
    """Validate an LLM configuration by testing the connection"""

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "Content-Type": "application/json",
        }

        # Support different auth header formats
        if "anthropic" in request.url.lower():
            headers["X-API-Key"] = request.api_key
            del headers["Authorization"]

        try:
            # Test with a simple completion request
            response = await client.post(
                f"{request.url}/chat/completions",
                headers=headers,
                json={
                    "model": request.model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5,
                },
                timeout=10.0,
            )
            response.raise_for_status()

            return {"valid": True}

        except httpx.HTTPStatusError as e:
            return {
                "valid": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}


# Alias for frontend compatibility
@router.post("/validate-llm")
async def validate_llm_alias(request: ValidationRequest):
    """Alias for /api/llm/validate to match frontend expectations"""
    return await validate_llm(request)


@router.post("/llm/models")
async def list_models(request: ModelsRequest):
    """List available models from an LLM provider"""

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "Content-Type": "application/json",
        }

        # Support different auth header formats
        if "anthropic" in request.url.lower():
            headers["X-API-Key"] = request.api_key
            del headers["Authorization"]

        try:
            # Try OpenAI-compatible models endpoint
            response = await client.get(
                f"{request.url}/models", headers=headers, timeout=10.0
            )
            response.raise_for_status()

            data = response.json()
            models = []

            # Extract model names based on response format
            if "data" in data:
                models = [model["id"] for model in data["data"]]
            elif isinstance(data, list):
                models = [
                    model["id"] if isinstance(model, dict) else str(model)
                    for model in data
                ]

            return {"models": models}

        except Exception as e:
            # Return empty list on error - user can still manually enter model names
            logger.warning(f"Failed to fetch models from {request.url}: {str(e)}")
            return {"models": []}
