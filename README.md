# DeutschLern AI

An AI-powered German language learning web application for CEFR levels A1–B1.

## Overview

DeutschLern AI is a personalised full-stack web app that adapts to each user's level, saved vocabulary, grammar progress, and exercise history. Built as part of the AI Engineering Weiterbildung course, Berlin 2025.

## Features (MVP — complete)

- **User Accounts** — registration, login, logout, JWT authentication
- **Grammar Theory** — structured A1 content across 6 topics with prev/next navigation
- **AI Exercises** — fill-in-the-blank and translation exercises, AI-graded with feedback
- **Vocabulary Manager** — save words with AI-generated example sentences, HTMX delete
- **Conversation Coach** — personalised text-based chat partner across 4 scenarios, session resume and delete
- **Dashboard** — live word count, exercise count, coach session count, last session date

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI 0.111+ |
| Database | PostgreSQL 16.x + SQLAlchemy 2.x (async) |
| Auth | python-jose + passlib (bcrypt + JWT cookie) |
| Frontend | Tailwind CSS 3.x, HTMX 1.9, Vanilla JS |
| Templating | Jinja2 via FastAPI |
| AI | OpenAI GPT-4o (coach + grading) & GPT-4o-mini (exercises + vocab) |
| Migrations | Alembic |

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16.x
- Node.js (for Tailwind CSS)
- An OpenAI API key

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd deutschlern-ai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install
```

### Configuration

Copy `.env.example` to `.env` and fill in your values:

```
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost/deutschlern_ai
OPENAI_API_KEY=sk-...
```

### Database Setup

```bash
# Create the database in PostgreSQL
psql -U postgres
CREATE DATABASE deutschlern_ai;
\q

# Run migrations
alembic upgrade head

# Seed A1 grammar topics
python seed.py
```

### Running the App

```bash
# Terminal 1 — Tailwind CSS watcher
npx tailwindcss -i app/static/css/input.css -o app/static/css/output.css --watch

# Terminal 2 — FastAPI dev server
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
deutschlern_ai/
├── app/
│   ├── main.py              # FastAPI app, routes, dashboard
│   ├── models.py            # SQLAlchemy models (7 tables)
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Async engine + session
│   ├── dependencies.py      # get_current_user JWT dependency
│   ├── routers/
│   │   ├── auth.py          # /auth/register, /login, /logout
│   │   ├── theory.py        # /theory, /theory/{id}
│   │   ├── exercises.py     # /exercises/{id}, /exercises/translate
│   │   ├── vocabulary.py    # /vocabulary, /vocabulary/save, /vocabulary/{id}
│   │   └── coach.py         # /coach, /coach/start, /coach/message, /coach/{id}
│   ├── services/
│   │   └── ai_service.py    # All OpenAI API calls (never call from routes)
│   ├── templates/           # Jinja2 templates per module
│   └── static/              # Tailwind output.css, main.js
├── tests/                   # pytest + httpx async test suite
├── migrations/              # Alembic auto-generated
├── config.py                # pydantic-settings
├── seed.py                  # Seeds 6 A1 grammar topics
└── requirements.txt
```

## Conversation Coach Scenarios

| Scenario | Description |
|---|---|
| Free | Open-ended conversation on any topic |
| Supermarket | Shopping at a German REWE store |
| Train Station | Buying tickets at Berlin Hauptbahnhof |
| Job Interview | Casual interview at a Berlin startup |

## Roadmap

### MVP (complete)
- User registration, login, logout
- A1 grammar theory — 6 topics with prev/next navigation
- AI fill-in-the-blank exercises with grading and feedback
- AI translation exercises with grading and corrections
- Vocabulary manager — save words, AI example sentences, delete
- Conversation coach — 4 scenarios, session history, resume, delete
- Dashboard — live stats (words, exercises, sessions, last session date)

### Week 4+
- A2 and B1 grammar content
- MCQ exercise type
- SM-2 spaced repetition flashcards
- Books and reading section with inline word lookup
- Voice chat (Whisper STT + OpenAI TTS)
- Full analytics dashboard
