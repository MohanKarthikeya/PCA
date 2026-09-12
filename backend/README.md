# PCA Backend

> **PCA (Personal Communication Assistant)** is a provider-agnostic AI backend that analyzes incoming messages, maintains long-term conversation memory, and generates intelligent multilingual replies using multiple LLM providers.

Built with **FastAPI**, **SQLAlchemy**, and a modular AI provider architecture.

---

# Features

- 🚀 FastAPI REST API
- 🤖 Provider-agnostic AI architecture
- 🧠 Long-term conversation memory
- 💬 AI-powered message analysis
- ✍️ AI-powered reply generation
- 🌍 Multilingual support
- 🔄 Switch AI providers using `.env`
- ⚡ Async SQLAlchemy
- 🗄 SQLite (PostgreSQL-ready)
- 📚 Automatic Swagger Documentation
- 📈 Structured JSON logging
- 🛡 Centralized exception handling
- 🔌 Dependency Injection architecture

---

# Architecture

```
                Incoming Messages
                       │
                       ▼
                 FastAPI Router
                       │
                       ▼
                  Service Layer
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     Database                 AI Service
          │                         │
          ▼                         ▼
    SQLite Database        Provider Factory
                                    │
         ┌──────────────┬───────────┼──────────────┐
         ▼              ▼           ▼              ▼
      Gemini         OpenAI      Claude       DeepSeek
                                          │
                                          ▼
                                       Ollama
```

---

# Folder Structure

```
backend/
│
├── api/
│   ├── deps.py
│   └── routers/
│
├── config/
│
├── database/
│
├── models/
│
├── prompts/
│
├── providers/
│
├── schemas/
│
├── services/
│
├── utils/
│
├── alembic/
│
├── main.py
├── seed.py
├── requirements.txt
└── .env.example
```

---

# AI Workflow

## Wake PCA (AI Call #1)

```
Unread Messages
        │
        ▼
Load Sender Profiles
        │
        ▼
Load Memory
        │
        ▼
Build Analysis Prompt
        │
        ▼
ONE AI API CALL
        │
        ▼
Parse JSON
        │
        ▼
Update Memory
        │
        ▼
Mark Messages Read
```

---

## Reply Generation (AI Call #2)

```
Target Message
        │
        ▼
Conversation History
        │
        ▼
Sender Memory
        │
        ▼
User Instruction
        │
        ▼
Build Reply Prompt
        │
        ▼
ONE AI API CALL
        │
        ▼
Save Draft Reply
```

---

# Supported AI Providers

Simply change

```env
ACTIVE_PROVIDER=
```

Supported values

```
mock
gemini
openai
claude
deepseek
ollama
```

No code changes required.

---

# Installation

## Clone

```bash
git clone https://github.com/YOUR_USERNAME/pca-backend.git

cd pca-backend/backend
```

---

## Create Virtual Environment

Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment

Copy

```bash
.env.example
```

to

```bash
.env
```

Fill in the API key for the provider you want to use.

Example

```env
ACTIVE_PROVIDER=gemini

GOOGLE_API_KEY=YOUR_API_KEY
```

---

# Database

Run migrations

```bash
alembic upgrade head
```

---

# Running

```bash
uvicorn main:app --reload
```

Server

```
http://127.0.0.1:8000
```

Swagger

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# API Endpoints

## Health

```
GET /health
```

---

## Messages

```
GET     /messages

GET     /messages/unread

POST    /messages

PUT     /messages/{id}/read

PUT     /messages/{id}/reply
```

---

## Senders

```
GET     /senders

POST    /senders

DELETE  /senders/{id}
```

---

## Memory

```
GET /memory

GET /memory/{sender_id}
```

---

## PCA

### AI Call #1

```
POST /pca/wake
```

Analyzes all unread messages in a single AI request.

---

### AI Call #2

```
POST /pca/reply
```

Generates a contextual multilingual reply.

---

# Configuration

| Variable | Description |
|-----------|-------------|
| ACTIVE_PROVIDER | Current AI Provider |
| DATABASE_URL | Database connection |
| AI_TIMEOUT_SECONDS | AI request timeout |
| AI_MAX_RETRIES | Retry attempts |
| DEBUG | Debug mode |
| LOG_LEVEL | Logging level |

---

# Design Principles

- Maximum **2 AI API calls** per interaction
- Provider-independent architecture
- Async-first implementation
- Modular service layer
- Dependency Injection
- Clean Architecture
- Structured logging
- Centralized error handling

---

# Tech Stack

- FastAPI
- SQLAlchemy 2.0
- Alembic
- SQLite
- Pydantic v2
- Google Gemini
- OpenAI
- Anthropic Claude
- DeepSeek
- Ollama

---

# Future Improvements

- PostgreSQL support
- Redis caching
- JWT Authentication
- WebSocket notifications
- Docker deployment
- Kubernetes deployment
- Background task queue
- Vector database support
- Semantic memory search
- User authentication
- Rate limiting
- Monitoring dashboard

---

# License

MIT License

---

# Author

**Mohan Ilapakurthi**

Built as part of the **VIT-AP Hackathon 2026**.