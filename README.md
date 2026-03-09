# Explaino

AI-powered learning tool that generates explanations and structured courses on any topic.

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Radix UI
- **Backend:** Python, FastAPI, OpenAI (via OpenRouter)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Setup

```bash
# Install all dependencies
make install

# Configure backend environment
cp app/.env.example app/.env
# Edit app/.env and add your OpenRouter API key
```

### Running

```bash
# Start both backend and frontend
make dev

# Or run them separately
make be   # Backend on http://localhost:8432
make fe   # Frontend on http://localhost:5173
```

## Available Commands

| Command          | Description                        |
| ---------------- | ---------------------------------- |
| `make dev`       | Start backend + frontend           |
| `make be`        | Start backend only                 |
| `make fe`        | Start frontend only                |
| `make install`   | Install all dependencies           |
| `make build`     | Production build (frontend)        |
| `make lint`      | Lint both backend and frontend     |
| `make test`      | Run backend tests                  |

## Project Structure

```
explaino/
├── app/                  # Backend (FastAPI)
│   └── src/
│       ├── main.py
│       ├── models/       # Pydantic models
│       ├── routes/       # API endpoints
│       └── services/     # Business logic
│           ├── ai_client.py        # Shared OpenAI client
│           ├── explain_service.py  # Explanation generation
│           ├── explain_storage.py  # Explanation storage
│           ├── course_service.py   # Course generation
│           └── course_storage.py   # Course storage
├── web/                  # Frontend (React + Vite)
│   └── src/
│       ├── api/          # API client
│       ├── components/   # UI components
│       ├── pages/        # Page components
│       ├── store/        # Zustand stores
│       └── types/        # TypeScript types
└── Makefile
```
