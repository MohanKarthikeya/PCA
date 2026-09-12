"""
GeminiProvider — uses google-generativeai SDK.
Activate with: ACTIVE_PROVIDER=gemini in .env
"""

import asyncio
import json
import re

from providers.base import AIProvider
from utils.exceptions import AIProviderError, AITimeoutError, InvalidAIResponseError, ProviderNotConfiguredError


class GeminiProvider(AIProvider):

    @property
    def name(self) -> str:
        return "gemini"

    def _get_client(self):
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError:
            raise AIProviderError(
                "google-generativeai package is not installed. "
                "Run: pip install google-generativeai"
            )

        from config.settings import get_settings
        settings = get_settings()

        if not settings.GOOGLE_API_KEY:
            raise ProviderNotConfiguredError("gemini")

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate(self, prompt: str) -> dict:
        from config.settings import get_settings
        settings = get_settings()

        model = self._get_client()

        try:
            # google-generativeai is sync; run in executor to stay async
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: model.generate_content(prompt)),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise AITimeoutError("gemini", settings.AI_TIMEOUT_SECONDS)
        except Exception as exc:
            raise AIProviderError(f"Gemini API error: {exc}") from exc

        raw_text = response.text
        return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from model output."""
    # Remove ```json ... ``` fences
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"Could not parse JSON from Gemini response: {exc}\nRaw: {text[:300]}"
        ) from exc
