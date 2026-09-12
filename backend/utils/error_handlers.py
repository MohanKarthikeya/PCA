"""
Centralized FastAPI exception handlers.
Maps PCAException subclasses and common HTTP exceptions to a
consistent JSON error envelope:

  {
    "error": true,
    "error_code": "MESSAGE_NOT_FOUND",
    "detail": "Message '...' not found.",
    "status_code": 404
  }
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.exceptions import PCAException

log = logging.getLogger("pca.errors")


def _error_body(status_code: int, error_code: str, detail: str) -> dict:
    return {
        "error": True,
        "error_code": error_code,
        "detail": detail,
        "status_code": status_code,
    }


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(PCAException)
    async def pca_exception_handler(request: Request, exc: PCAException):
        log.warning(
            "PCA domain error",
            extra={"path": request.url.path, "error_code": exc.error_code,
                   "detail": exc.detail},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.status_code, exc.error_code, exc.detail),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        log.warning(
            "HTTP error",
            extra={"path": request.url.path, "status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.status_code, "HTTP_ERROR", str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = exc.errors()
        log.warning(
            "Request validation error",
            extra={"path": request.url.path, "errors": errors},
        )
        return JSONResponse(
            status_code=422,
            content=_error_body(
                422,
                "VALIDATION_ERROR",
                f"Request validation failed: {errors}",
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        log.error(
            "Unhandled exception",
            extra={"path": request.url.path, "error": str(exc)},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=_error_body(500, "INTERNAL_ERROR",
                                "An unexpected server error occurred."),
        )
