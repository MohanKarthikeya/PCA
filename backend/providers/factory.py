"""
Provider factory — resolves ACTIVE_PROVIDER env var to a concrete AIProvider.

Adding a new provider requires only:
  1. Creating a new file in providers/
  2. Adding one entry to the registry dict below
  3. Setting ACTIVE_PROVIDER=<name> in .env

Zero changes elsewhere in the project.
"""

from functools import lru_cache

from providers.base import AIProvider
from utils.exceptions import AIProviderError


@lru_cache(maxsize=1)
def get_provider() -> AIProvider:
    """
    Return the singleton AIProvider instance for the active provider.
    Cached after first call — provider switches require a process restart.
    """
    from config.settings import get_settings
    settings = get_settings()
    name = settings.ACTIVE_PROVIDER.lower()

    registry: dict[str, type[AIProvider]] = _build_registry()

    if name not in registry:
        raise AIProviderError(
            f"Unknown ACTIVE_PROVIDER='{name}'. "
            f"Valid options: {list(registry.keys())}"
        )

    return registry[name]()


def _build_registry() -> dict[str, type[AIProvider]]:
    """Lazily build the registry to avoid import errors for unused providers."""
    from providers.mock_provider import MockProvider
    from providers.gemini_provider import GeminiProvider
    from providers.openai_provider import OpenAIProvider
    from providers.claude_provider import ClaudeProvider
    from providers.deepseek_provider import DeepSeekProvider
    from providers.ollama_provider import OllamaProvider

    return {
        "mock": MockProvider,
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "deepseek": DeepSeekProvider,
        "ollama": OllamaProvider,
    }
