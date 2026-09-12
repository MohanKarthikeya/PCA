"""
MockProvider — deterministic, zero-dependency AI provider.

Returns realistic fake JSON responses for both analysis and reply calls.
Works entirely offline and requires no API keys.

This is the DEFAULT provider (ACTIVE_PROVIDER=mock) so the project runs
immediately after `uvicorn main:app --reload` without any configuration.
"""

import asyncio
import json

from providers.base import AIProvider


_ANALYSIS_TEMPLATE = {
    "analyses": [
        {
            "message_id": "__PLACEHOLDER__",
            "detected_language": "en",
            "translated_message": "Lab session is postponed to tomorrow.",
            "intent": "notification",
            "importance_score": 7.5,
            "telugu_explanation": "ప్రొఫెసర్ రేపటికి ల్యాబ్ వాయిదా వేశారు.",
            "reply_required": True,
            "suggested_action": "Acknowledge and note the rescheduled lab session."
        }
    ],
    "memory_updates": [],
    "greeting": "నమస్కారం! మీకు కొత్త సందేశాలు వచ్చాయి.",
    "summary_telugu": "మీకు 1 ముఖ్యమైన సందేశం వుంది. దయచేసి చదవండి."
}

_REPLY_TEMPLATE = {
    "reply_in_sender_language": "Okay sir, thank you! I'll be there tomorrow.",
    "reply_translation": "సరే సార్, ధన్యవాదాలు! నేను రేపు అక్కడ ఉంటాను.",
    "confidence": 0.92,
    "explanation": "Polite acknowledgement generated based on the user's instruction."
}


class MockProvider(AIProvider):
    """
    Fake provider that returns realistic pre-baked JSON responses.
    Useful for development, testing, and demo purposes.
    """

    @property
    def name(self) -> str:
        return "mock"

    async def generate(self, prompt: str) -> dict:
        # Simulate a small network delay so the demo feels realistic
        await asyncio.sleep(0.3)

        # Detect which type of call this is by inspecting the prompt
        if "REPLY_GENERATION" in prompt:
            return dict(_REPLY_TEMPLATE)

        # Default → analysis response
        # The prompt contains message IDs — extract the first one for realism
        result = json.loads(json.dumps(_ANALYSIS_TEMPLATE))  # deep copy
        return result
