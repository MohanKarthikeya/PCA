"""
OllamaProvider — calls a locally running Ollama instance via HTTP.
Activate with: ACTIVE_PROVIDER=ollama in .env
Set OLLAMA_BASE_URL and OLLAMA_MODEL in .env.
"""

import asyncio
import json
import re

import httpx

from providers.base import AIProvider
from utils.exceptions import AIProviderError, AITimeoutError, InvalidAIResponseError


class OllamaProvider(AIProvider):

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, prompt: str) -> dict:
        from config.settings import get_settings
        settings = get_settings()

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(
                base_url=settings.OLLAMA_BASE_URL,
                timeout=settings.AI_TIMEOUT_SECONDS,
            ) as client:
                response = await client.post("/api/generate", json=payload)
                response.raise_for_status()
        except httpx.TimeoutException:
            raise AITimeoutError("ollama", settings.AI_TIMEOUT_SECONDS)
        except httpx.HTTPStatusError as exc:
            raise AIProviderError(
                f"Ollama HTTP error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except Exception as exc:
            raise AIProviderError(
                f"Ollama connection error: {exc}. "
                f"Is Ollama running at {settings.OLLAMA_BASE_URL}?"
            ) from exc

        data = response.json()
        raw_text = data.get("response", "")
        return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"Could not parse JSON from Ollama response: {exc}\nRaw: {text[:300]}"
        ) from exc
