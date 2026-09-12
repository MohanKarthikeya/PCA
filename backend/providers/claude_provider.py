"""
ClaudeProvider — uses anthropic SDK.
Activate with: ACTIVE_PROVIDER=claude in .env
"""

import asyncio
import json
import re

from providers.base import AIProvider
from utils.exceptions import AIProviderError, AITimeoutError, InvalidAIResponseError, ProviderNotConfiguredError


class ClaudeProvider(AIProvider):

    @property
    def name(self) -> str:
        return "claude"

    def _get_client(self):
        try:
            import anthropic  # type: ignore
        except ImportError:
            raise AIProviderError(
                "anthropic package is not installed. Run: pip install anthropic"
            )

        from config.settings import get_settings
        settings = get_settings()

        if not settings.ANTHROPIC_API_KEY:
            raise ProviderNotConfiguredError("claude")

        return anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate(self, prompt: str) -> dict:
        from config.settings import get_settings
        settings = get_settings()
        client = self._get_client()

        try:
            response = await asyncio.wait_for(
                client.messages.create(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=4096,
                    system=(
                        "You are PCA, a multilingual personal communication assistant. "
                        "Always respond with valid JSON only, no prose."
                    ),
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise AITimeoutError("claude", settings.AI_TIMEOUT_SECONDS)
        except Exception as exc:
            raise AIProviderError(f"Claude API error: {exc}") from exc

        raw_text = response.content[0].text
        return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"Could not parse JSON from Claude response: {exc}\nRaw: {text[:300]}"
        ) from exc
