# src/multibrain/api/routes/router.py

import logging
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from typing import Dict, Any

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


async def get_response_from_openai_compatible(
    host: str,
    model_name: str,
    query_request: QueryRequest,
    source_name: str,
    color: str,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Get response from OpenAI-compatible endpoint (replaces Ollama)"""
    logger = logging.getLogger(__name__)

    headers = {"Content-Type": "application/json"}

    # Add API key if provided
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": query_request.query}],
        "stream": False,
    }

    async with httpx.AsyncClient() as client:
        try:
            # Assume OpenAI-compatible endpoint
            url = (
                f"{host}/v1/chat/completions"
                if not host.endswith("/chat/completions")
                else host
            )

            response = await client.post(
                url, headers=headers, json=payload, timeout=60.0
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            logger.debug(f"Extracted content from {host}: {content}")
            return {
                "response": content,
                "source": source_name,
                "model": model_name,
                "host": host,
                "color": color,
            }
        except Exception as e:
            logger.error(f"Error processing request for {host}: {e}")
            return {"error": str(e), "source": source_name, "host": host}


# Legacy endpoint removed - the old Streamlit app that used this endpoint has been removed
