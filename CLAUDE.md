# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SIGS Design Agent Game Demo — an AR-enabled campus exploration and co-creation platform for Tsinghua SIGS (Shenzhen). Combines virtual exploration, gamified learning, and AI-assisted design to deepen campus engagement. The authoritative development rules are in `开发规则.md` (versioned); always follow that document when it conflicts with anything else.

## Current Status

Design and planning phase. Backend/`frontend`/`data`/`test` directories are scaffolds (`.gitkeep` only). Working HTML prototypes live in `demo_doc/demo/`. No `package.json` or `pyproject.toml` yet.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy + asyncpg (async PostgreSQL)
- **Package manager:** uv (Python), npm (frontend)
- **Frontend:** Native HTML / CSS / JavaScript
- **Linting:** Ruff (backend)
- **Database:** Cloud-hosted PostgreSQL (no local DB)

## Common Commands

```bash
# Backend — create venv and install deps (first time)
cd backend && uv sync

# Backend — run dev server
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8888 --reload

# Lint — check
ruff check .
# Lint — auto-fix
ruff check --fix .
# Lint — format
ruff format .
```

Frontend is static HTML; open files directly or serve via FastAPI. For public access, use a tunnel tool.

## Repository Structure

```
backend/     Python/FastAPI backend
frontend/    Static HTML/CSS/JS frontend
data/        Data artifacts (actual data in cloud DB)
test/        Tests — mirrors source path structure
temp/        Scratch files, logs, cache (gitignored)
doc/         Design documents (game interaction, etc.)
demo_doc/    Demo prototypes and reference docs
.env.example Environment variable template
开发规则.md   Authoritative development rules (Chinese)
```

## Architecture & Conventions

### API Design

- RESTful, JSON, prefix `/api/v1/`, plural lowercase nouns
- Auth via `X-API-Key` header (stored in env vars)
- Unified response: `{"code": 0, "message": "success", "data": {...}}`
- Error codes: `0` success, `40001` bad params, `40101` auth, `40401` not found, `50001` server error

### Naming

| Scope | Style | Example |
|---|---|---|
| Python files, vars, funcs | snake_case | `user_service.py`, `get_user_by_id` |
| Python classes | PascalCase | `UserService` |
| Python constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| HTML/CSS/JS files, CSS classes | kebab-case | `game-board.html`, `.game-container` |
| JS vars/funcs | camelCase | `getUserData` |
| JS constants | UPPER_SNAKE_CASE | `API_BASE_URL` |

### Code Limits

- Functions ≤ 200 lines, files ≤ 800 lines
- No bare `except` — always specify exception type
- Parameterized SQL only — no string concatenation
- Secrets via environment variables only — never hardcode or log

### Testing

- One test file per source file, paths mirror the source tree
  - `backend/database/serve.py` → `test/backend/database/test_serve.py`
- Features must pass tests before merge

## Git Workflow

- `main` — active development branch
- `serve` — stable/production branch (merge here only after tests pass)
- `feature/xxx` — optional feature branches from main
- Commit format: `<type>: <description>` (types: feat, fix, refactor, test, docs, style, chore)
- No force-push to `serve`

## Environment Variables

Copy `.env.example` to `.env` and fill in real values. Required: `DATABASE_URL`, `DATABASE_NAME`, `API_KEY`, `API_HOST`, `API_PORT`, `FRONTEND_URL`. Never commit `.env`.
