# Explaino Backend

Backend API for Explaino - AI-powered explanation generation with tree spanning structure.

## Overview

This Python backend provides RESTful API endpoints for the Explaino frontend application. It handles:
- Receiving text and context from the frontend
- Generating AI-powered explanations using OpenAI
- Managing explanation tree structures
- Handling nested explanation requests

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **OpenAI**: AI model integration for generating explanations
- **Pydantic**: Data validation and settings management
- **Poetry**: Dependency management

## Project Structure

```
app/
├── pyproject.toml          # Poetry configuration and dependencies
├── README.md               # This file
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── src/
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration and settings
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   └── explanation.py # Explanation data models
│   ├── routes/            # API route handlers
│   │   ├── __init__.py
│   │   └── explanation.py # Explanation endpoints
│   └── services/          # Business logic
│       ├── __init__.py
│       └── ai_service.py  # AI explanation generation
└── tests/                 # Test files
    └── __init__.py
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Running the Application

Development mode:
```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/explain
Generate an explanation for given text.

**Request Body:**
```json
{
  "text": "string to explain",
  "context": "optional context",
  "parent_id": "optional parent explanation ID"
}
```

**Response:**
```json
{
  "id": "explanation_id",
  "text": "original text",
  "explanation": "AI generated explanation",
  "parent_id": "parent_id or null",
  "created_at": "timestamp"
}
```

## Development

### Code Formatting
```bash
poetry run black src/
```

### Linting
```bash
poetry run ruff check src/
```

### Running Tests
```bash
poetry run pytest
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:5173)

## License

MIT
