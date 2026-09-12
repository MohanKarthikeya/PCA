"""
OpenAIProvider — uses the openai SDK (v1+).
Activate with: ACTIVE_PROVIDER=openai in .env
"""

import json
import re

from providers.base import AIProvider
from utils.exceptions import AIProviderError, AITimeoutError, InvalidAIResponseError, ProviderNotConfiguredError


class OpenAIProvider(AIProvider):

    @property
    def name(self) -> str:
        return "openai"

    def _get_client(self):
        try:
            from openai import AsyncOpenAI  # type: ignore
        except ImportError:
            raise AIProviderError(
                "openai package is not installed. Run: pip install openai"
            )

        from config.settings import get_settings
        settings = get_settings()

        if not settings.OPENAI_API_KEY:
            raise ProviderNotConfiguredError("openai")

        return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, prompt: str) -> dict:
        from config.settings import get_settings
        import asyncio

        settings = get_settings()
        client = self._get_client()

        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are PCA, a multilingual communication assistant. Always respond with valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                ),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise AITimeoutError("openai", settings.AI_TIMEOUT_SECONDS)
        except Exception as exc:
            raise AIProviderError(f"OpenAI API error: {exc}") from exc

        raw_text = response.choices[0].message.content or ""
        return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"Could not parse JSON from OpenAI response: {exc}\nRaw: {text[:300]}"
        ) from exc
