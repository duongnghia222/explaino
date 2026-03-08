.PHONY: dev be fe install install-be install-fe lint lint-be lint-fe build test

# Start both backend and frontend
dev:
	@echo "Starting backend and frontend..."
	@make be & make fe & wait

# Backend
be:
	cd app && uv run uvicorn src.main:app --reload --port 8000

install-be:
	cd app && uv sync

lint-be:
	cd app && uv run ruff check src

test:
	cd app && uv run pytest

# Frontend
fe:
	cd web && npm run dev

install-fe:
	cd web && npm install

lint-fe:
	cd web && npm run lint

build:
	cd web && npm run build

# All
install: install-be install-fe

lint: lint-be lint-fe
