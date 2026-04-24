# GitHub Copilot Instructions

> SIGS Design Agent Game Demo — Project-Specific Instructions for GitHub Copilot

## Project Overview

**Project**: AR-enabled campus exploration and co-creation platform for Tsinghua SIGS (Shenzhen)
**Tech Stack**: Python/FastAPI backend, native HTML/CSS/JS frontend, PostgreSQL cloud DB
**Package Manager**: uv (Python), npm (frontend)
**Linting**: Ruff (backend)

## Code Style Guidelines

### Python
- Use `snake_case` for files, variables, and functions
- Use `PascalCase` for class names
- Use `UPPER_SNAKE_CASE` for constants
- Add docstrings to all functions and classes
- Maximum function length: 200 lines
- Maximum file length: 800 lines
- Never use bare `except` — always specify exception type

### JavaScript
- Use `camelCase` for variables and functions
- Use `UPPER_SNAKE_CASE` for constants
- Use `kebab-case` for file names and CSS class names
- Add JSDoc comments for functions

### API Design
- All API routes use `/api/v1/` prefix with plural lowercase nouns
- Example: `/api/v1/users`, `/api/v1/designs`, `/api/v1/sessions`
- Unified response format:
  - Success: `{"code": 0, "message": "success", "data": {...}}`
  - Error: `{"code": <code>, "message": "<description>", "data": null}`
- Authentication via `X-API-Key` header
- Error codes: 0 (success), 40001 (bad params), 40101 (auth), 40401 (not found), 50001 (server error)

### SQL Security
- Always use parameterized queries
- Never concatenate SQL strings with user input

## Testing Conventions

- One test file per source file
- Test paths mirror source paths:
  - `backend/database/serve.py` → `test/backend/database/test_serve.py`
- Use `pytest` for testing
- Use `pytest-asyncio` for async tests
- Use `httpx` for HTTP client testing

## File Naming

| Type | Format | Examples |
|------|--------|----------|
| Python files | `snake_case.py` | `user_service.py` |
| HTML/CSS/JS files | `kebab-case.{ext}` | `game-board.html`, `api-client.js` |
| Test files | `test_<name>.py` | `test_user_service.py` |
| API routes | `/api/v1/<plural>` | `/api/v1/designs` |

## Git Commit Format

```
<type>: <description>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`
Example: `feat: add user registration endpoint`

## Security Rules

- ALL external input must be validated
- NEVER hardcode secrets (API keys, passwords)
- Use environment variables for sensitive data
- Required env vars: `DATABASE_URL`, `DATABASE_NAME`, `API_KEY`, `API_HOST`, `API_PORT`, `FRONTEND_URL`

## When Writing Documents

1. Read `doc/00_文档存放规则.md` first
2. Document type determines directory:
   - Reports/audits → `doc/03_reports/`
   - Work plans → `doc/04_plans/`
   - Architecture → `doc/01_architecture/`
   - Product design → `doc/02_product/`
3. Use naming: `[description]_[YYYY-MM-DD].md` for reports and plans
4. Update `doc/INDEX.md` with new document link

## Environment Setup

```bash
# Backend setup
cd backend && uv sync

# Run dev server
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Lint code
ruff check .
ruff check --fix .
ruff format .

# Run tests
pytest
```

## Authoritative Rules

When rules conflict, follow this priority:
1. `开发规则.md` (highest priority — Chinese)
2. `AGENT.md`
3. This file
4. Other documentation

## Checklist Before Completing Tasks

- [ ] Code follows naming conventions
- [ ] Functions ≤ 200 lines, files ≤ 800 lines
- [ ] No bare `except` clauses
- [ ] SQL uses parameterized queries
- [ ] Secrets via environment variables only
- [ ] Test file created (mirrors source path)
- [ ] Passes `ruff check .`
- [ ] If document created, follows `doc/00_文档存放规则.md`
