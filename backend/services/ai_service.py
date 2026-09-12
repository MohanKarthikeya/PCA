"""
AIService — orchestrates all AI interactions.

Responsibilities:
  - Build prompts (delegates to prompts/)
  - Call the active provider (via providers/factory.py)
  - Parse and validate the JSON response
  - Retry on transient failures (max AI_MAX_RETRIES)
  - Normalize output into typed schemas
  - Log provider used and latency

This service is the ONLY place in the codebase that calls the AI provider.
All other services are purely database operations.
"""

import asyncio
import logging
from typing import Any

from config.settings import get_settings
from providers.factory import get_provider
from prompts.analysis_prompt import build_analysis_prompt
from prompts.reply_prompt import build_reply_prompt
from schemas.pca import MessageAnalysis, MemoryUpdate, WakeResponse, ReplyResponse as PCAReplyResponse
from utils.exceptions import AIProviderError, InvalidAIResponseError
from utils.logger import AILatencyLogger

log = logging.getLogger("pca.ai_service")
settings = get_settings()


class AIService:

    async def analyze_messages(
        self,
        messages: list[dict[str, Any]],
        senders: dict[str, dict[str, Any]],
        memory: dict[str, dict[str, Any]],
        user_language: str = "en",
    ) -> WakeResponse:
        """
        AI Call #1 — analyze all unread messages in a single API call.

        Returns a fully-validated WakeResponse.
        """
        provider = get_provider()

        prompt = build_analysis_prompt(
            messages=messages,
            senders=senders,
            memory=memory,
            user_language=user_language,
        )

        raw = await self._call_with_retry(provider, prompt)

        return self._parse_analysis_response(raw, provider.name, len(messages))

    async def generate_reply(
        self,
        original_message: dict[str, Any],
        sender: dict[str, Any],
        user_instruction: str,
        conversation_history: list[dict[str, Any]],
        memory: dict[str, Any] | None,
        message_id: str,
        user_language: str = "en",
    ) -> PCAReplyResponse:
        """
        AI Call #2 — generate a contextual reply in the sender's language.

        Returns a fully-validated PCAReplyResponse.
        """
        provider = get_provider()

        prompt = build_reply_prompt(
            original_message=original_message,
            sender=sender,
            user_instruction=user_instruction,
            conversation_history=conversation_history,
            memory=memory,
            user_language=user_language,
        )

        raw = await self._call_with_retry(provider, prompt)

        return self._parse_reply_response(raw, provider.name, message_id)

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _call_with_retry(self, provider, prompt: str) -> dict:
        """
        Call the provider with exponential back-off retry.
        Raises AIProviderError after AI_MAX_RETRIES failures.
        """
        last_exc: Exception | None = None

        for attempt in range(1, settings.AI_MAX_RETRIES + 2):  # +2 = initial + retries
            try:
                with AILatencyLogger(provider.name, "generate"):
                    result = await provider.generate(prompt)
                log.info(
                    "AI call succeeded",
                    extra={"provider": provider.name, "attempt": attempt},
                )
                return result
            except InvalidAIResponseError:
                # Malformed JSON — retrying might help if it was intermittent
                raise
            except AIProviderError as exc:
                last_exc = exc
                if attempt <= settings.AI_MAX_RETRIES:
                    wait = 2 ** (attempt - 1)  # 1s, 2s, 4s ...
                    log.warning(
                        "AI call failed, retrying",
                        extra={"provider": provider.name, "attempt": attempt, "wait_s": wait},
                    )
                    await asyncio.sleep(wait)

        raise AIProviderError(
            f"AI provider '{provider.name}' failed after "
            f"{settings.AI_MAX_RETRIES + 1} attempts. Last error: {last_exc}"
        )

    def _parse_analysis_response(
        self, raw: dict, provider_name: str, message_count: int
    ) -> WakeResponse:
        try:
            analyses = [
                MessageAnalysis(**item)
                for item in raw.get("analyses", [])
            ]
            memory_updates = [
                MemoryUpdate(**upd)
                for upd in raw.get("memory_updates", [])
            ]
            return WakeResponse(
                provider_used=provider_name,
                messages_analyzed=message_count,
                analyses=analyses,
                memory_updates=memory_updates,
                greeting=raw.get("greeting", "నమస్కారం!"),
                summary_telugu=raw.get("summary_telugu", ""),
            )
        except Exception as exc:
            raise InvalidAIResponseError(
                f"Analysis response did not match expected schema: {exc}"
            ) from exc

    def _parse_reply_response(
        self, raw: dict, provider_name: str, message_id: str
    ) -> PCAReplyResponse:
        try:
            return PCAReplyResponse(
                provider_used=provider_name,
                message_id=message_id,
                reply_in_sender_language=raw["reply_in_sender_language"],
                reply_translation=raw.get("reply_translation", ""),
                confidence=float(raw.get("confidence", 0.85)),
                explanation=raw.get("explanation"),
                reply_id="",  # Will be filled by the router after DB save
            )
        except Exception as exc:
            raise InvalidAIResponseError(
                f"Reply response did not match expected schema: {exc}"
            ) from exc
