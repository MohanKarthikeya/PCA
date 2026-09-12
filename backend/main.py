"""
PCA — Personal Communication Assistant
FastAPI application entry point.

Run with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import messages, senders, pca, memory
from config.settings import get_settings
from database.session import create_tables
from utils.error_handlers import register_exception_handlers
from utils.logger import setup_logging, get_logger

# Initialise logging before anything else
setup_logging()
log = get_logger("pca.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    log.info(
        "PCA backend starting",
        extra={"provider": settings.ACTIVE_PROVIDER, "debug": settings.DEBUG},
    )
    # Create database tables on first run (idempotent)
    await create_tables()
    log.info("Database tables ready")
    yield
    log.info("PCA backend shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "PCA (Personal Communication Assistant) backend API.\n\n"
        "**AI Calls per session:** max 2\n"
        "- `POST /pca/wake` → AI Call #1 (message analysis)\n"
        "- `POST /pca/reply` → AI Call #2 (reply generation)\n\n"
        f"**Active AI Provider:** `{settings.ACTIVE_PROVIDER}`"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(messages.router)
app.include_router(senders.router)
app.include_router(pca.router)
app.include_router(memory.router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.ACTIVE_PROVIDER,
    }


@app.get("/", tags=["Health"], summary="Root")
async def root():
    return {
        "message": "PCA Backend is running. Visit /docs for API documentation.",
        "docs": "/docs",
        "redoc": "/redoc",
    }
