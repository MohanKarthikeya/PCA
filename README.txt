PCA/
    frontend/
    ├── Dashboard
    │
    ├── Messages
    │      ├── Contact List
    │      ├── Conversation
    │      └── Message Composer
    │
    ├── User Profile
    │
    ├── AI Decisions
    │
    ├── Memory Viewer
    │
    ├── Settings
    │
    └── Logs

    backend/
    ├── api/
    │   ├── __init__.py
    │   ├── deps.py                  # Dependency injection (DB session, etc.)
    │   ├── routers/
    │   │   ├── messages.py
    │   │   ├── senders.py
    │   │   ├── pca.py               # /pca/wake and /pca/reply
    │   │   └── memory.py
    ├── config/
    │   ├── __init__.py
    │   └── settings.py              # Pydantic BaseSettings, .env loader
    ├── database/
    │   ├── __init__.py
    │   ├── base.py                  # SQLAlchemy declarative base
    │   └── session.py               # async engine + session factory
    ├── models/
    │   ├── __init__.py
    │   ├── user.py
    │   ├── sender.py
    │   ├── message.py
    │   ├── memory.py
    │   └── reply.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── user.py
    │   ├── sender.py
    │   ├── message.py
    │   ├── memory.py
    │   ├── reply.py
    │   └── pca.py                   # Wake/Reply request+response schemas
    ├── services/
    │   ├── __init__.py
    │   ├── message_service.py
    │   ├── sender_service.py
    │   ├── memory_service.py
    │   ├── reply_service.py
    │   └── ai_service.py            # Orchestrates AI calls
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py                  # AIProvider abstract base class
    │   ├── mock_provider.py         # Default: deterministic mock
    │   ├── gemini_provider.py
    │   ├── openai_provider.py
    │   ├── claude_provider.py
    │   ├── deepseek_provider.py
    │   └── ollama_provider.py
    ├── prompts/
    │   ├── __init__.py
    │   ├── analysis_prompt.py       # Wake PCA prompt builder
    │   └── reply_prompt.py          # Reply generation prompt builder
    ├── utils/
    │   ├── __init__.py
    │   ├── exceptions.py            # Custom exception classes
    │   ├── error_handlers.py        # FastAPI exception handlers
    │   └── logger.py                # Structured logging setup
    ├── alembic/
    │   └── versions/                # DB migrations
    ├── alembic.ini
    ├── seed.py                      # Sample SQLite seed data
    ├── main.py                      # FastAPI app entry point
    ├── requirements.txt
    ├── .env.example
    └── README.md
