"""
Custom exception hierarchy for PCA backend.
All domain errors inherit from PCAException so they can be caught broadly
and handled uniformly by the centralized error handler.
"""


class PCAException(Exception):
    """Base exception for all PCA application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = "An unexpected error occurred.") -> None:
        self.detail = detail
        super().__init__(detail)


# ── Resource Errors ───────────────────────────────────────────────────────────

class NotFoundError(PCAException):
    status_code = 404
    error_code = "NOT_FOUND"


class MessageNotFoundError(NotFoundError):
    error_code = "MESSAGE_NOT_FOUND"

    def __init__(self, message_id: str) -> None:
        super().__init__(f"Message '{message_id}' not found.")


class SenderNotFoundError(NotFoundError):
    error_code = "SENDER_NOT_FOUND"

    def __init__(self, sender_id: str) -> None:
        super().__init__(f"Sender '{sender_id}' not found.")


class MemoryNotFoundError(NotFoundError):
    error_code = "MEMORY_NOT_FOUND"

    def __init__(self, sender_id: str) -> None:
        super().__init__(f"Memory for sender '{sender_id}' not found.")


class UserNotFoundError(NotFoundError):
    error_code = "USER_NOT_FOUND"

    def __init__(self, user_id: str) -> None:
        super().__init__(f"User '{user_id}' not found.")


# ── Validation Errors ─────────────────────────────────────────────────────────

class ValidationError(PCAException):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class InvalidRequestError(ValidationError):
    error_code = "INVALID_REQUEST"


# ── AI Provider Errors ────────────────────────────────────────────────────────

class AIProviderError(PCAException):
    status_code = 502
    error_code = "AI_PROVIDER_ERROR"


class AITimeoutError(AIProviderError):
    error_code = "AI_TIMEOUT"

    def __init__(self, provider: str, timeout: int) -> None:
        super().__init__(
            f"AI provider '{provider}' timed out after {timeout}s."
        )


class InvalidAIResponseError(AIProviderError):
    error_code = "INVALID_AI_RESPONSE"

    def __init__(self, detail: str = "AI returned a malformed response.") -> None:
        super().__init__(detail)


class ProviderNotConfiguredError(AIProviderError):
    error_code = "PROVIDER_NOT_CONFIGURED"
    status_code = 503

    def __init__(self, provider: str) -> None:
        super().__init__(
            f"AI provider '{provider}' is not configured. "
            "Please set the required API key in your .env file."
        )
