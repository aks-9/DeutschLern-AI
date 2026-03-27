# DeutschLern AI

An AI-powered German language learning web application for CEFR levels A1–B1.

## Overview

DeutschLern AI is a personalised full-stack web app that adapts to each user's level, saved vocabulary, grammar progress, and exercise history. Built as part of the AI Engineering Weiterbildung course, Berlin 2025.

## Features (MVP)

- **User Accounts** — registration, login, logout, level tracking
- **Grammar Theory** — structured A1 content across 6 topics
- **AI Exercises** — fill-in-the-blank and translation exercises, AI-graded
- **Vocabulary Manager** — save words with AI-generated example sentences
- **Conversation Coach** — personalised text-based chat partner (4 scenarios)
- **Dashboard** — word count, exercise count, progress overview

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI 0.111+ |
| Database | PostgreSQL 16.x + SQLAlchemy 2.x |
| Auth | python-jose + passlib (JWT) |
| Frontend | Tailwind CSS, HTMX, Vanilla JS |
| AI | OpenAI GPT-4o & GPT-4o-mini |
| Migrations | Alembic |

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16.x
- Node.js (for Tailwind CSS)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd deutschlern_ai

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
alembic init migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# Seed grammar topics
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
│   ├── __init__.py          # App factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes/              # Blueprints (auth, theory, exercises, vocab, coach)
│   ├── services/
│   │   └── ai_service.py    # All OpenAI API calls
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS and JS
├── migrations/
├── docs/                    # Project documentation
├── config.py
├── seed.py
├── run.py
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

- A2 and B1 grammar content
- SM-2 spaced repetition flashcards
- Books and reading section with inline word lookup
- Voice chat (Whisper STT + OpenAI TTS)
- Full analytics dashboard
