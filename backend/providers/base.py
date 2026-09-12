"""
Abstract base class for all AI providers.

Every provider MUST implement `generate(prompt: str) -> dict`.
The returned dict must always be valid JSON-serialisable Python.

Switching providers requires ZERO changes outside this package —
simply set ACTIVE_PROVIDER in .env.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Interface that every AI provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name used in logs and responses."""
        ...

    @abstractmethod
    async def generate(self, prompt: str) -> dict:
        """
        Send `prompt` to the underlying LLM and return the parsed JSON dict.

        Implementations are responsible for:
        - Authentication with their respective API
        - Sending the request (async)
        - Extracting and parsing the JSON from the raw response
        - Raising AIProviderError / AITimeoutError on failure

        Args:
            prompt: The fully-formed prompt string built by a prompt module.

        Returns:
            A Python dict representing the structured JSON the model returned.
        """
        ...
