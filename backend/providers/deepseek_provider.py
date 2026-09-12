"""
DeepSeekProvider — uses DeepSeek's OpenAI-compatible API.
Activate with: ACTIVE_PROVIDER=deepseek in .env
"""

import asyncio
import json
import re

from providers.base import AIProvider
from utils.exceptions import AIProviderError, AITimeoutError, InvalidAIResponseError, ProviderNotConfiguredError

_DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class DeepSeekProvider(AIProvider):

    @property
    def name(self) -> str:
        return "deepseek"

    def _get_client(self):
        try:
            from openai import AsyncOpenAI  # type: ignore
        except ImportError:
            raise AIProviderError(
                "openai package is not installed (required for DeepSeek). "
                "Run: pip install openai"
            )

        from config.settings import get_settings
        settings = get_settings()

        if not settings.DEEPSEEK_API_KEY:
            raise ProviderNotConfiguredError("deepseek")

        return AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=_DEEPSEEK_BASE_URL,
        )

    async def generate(self, prompt: str) -> dict:
        from config.settings import get_settings
        settings = get_settings()
        client = self._get_client()

        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=settings.DEEPSEEK_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are PCA, a multilingual communication assistant. Always respond with valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                ),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise AITimeoutError("deepseek", settings.AI_TIMEOUT_SECONDS)
        except Exception as exc:
            raise AIProviderError(f"DeepSeek API error: {exc}") from exc

        raw_text = response.choices[0].message.content or ""
        return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"Could not parse JSON from DeepSeek response: {exc}\nRaw: {text[:300]}"
        ) from exc
