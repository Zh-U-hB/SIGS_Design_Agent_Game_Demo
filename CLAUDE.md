# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SIGS Design Agent Game Demo — an AR-enabled campus exploration and co-creation platform for Tsinghua SIGS (Shenzhen). Combines virtual exploration, gamified learning, and AI-assisted design to deepen campus engagement.

**Authoritative Rules**: `开发规则.md` (versioned) is the authoritative development rules document. Always follow that document when it conflicts with anything else.

## Current Status

Design and planning phase. Backend and frontend code structure is established. Working HTML prototypes live in `demo_doc/demo/`. Three core AI services (agent_service, image_service, model3d_service) are stubs pending implementation.

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
doc/         Design documents (organized by category)
demo_doc/    Demo prototypes and reference docs
dev_doc/     Development temporary docs (PR reviews, notes)
.env.example Environment variable template
开发规则.md   Authoritative development rules (Chinese)
AGENT.md     Agent development guidelines
CLAUDE.md    This file — Claude Code specific guidance
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

---

## Document Management (Claude Code Specific)

### Writing Documents

When you are asked to "write a document" or "generate a report":

1. **Read the storage rules first**: Always read `doc/00_文档存放规则.md` before writing any document
2. **Determine document type** based on user request:
   - "code report", "audit", "review" → `doc/03_reports/`
   - "work plan", "todo", "follow-up work" → `doc/04_plans/`
   - "architecture design", "technical plan" → `doc/01_architecture/`
   - "interaction design", "UX" → `doc/02_product/`
   - "meeting notes", "decision record" → `doc/05_meetings/`
3. **Use standard naming format**: `[description]_[YYYY-MM-DD].md` (date required for reports and plans)
4. **Include standard header metadata**:
   ```markdown
   # Document Title

   > **Version**: X.Y.Z
   > **Updated**: YYYY-MM-DD
   > **Author**: Author name
   > **Status**: [Draft/In Review/Published/Archived]
   > **Related**: [Related doc](path)
   ```
5. **Update** `doc/INDEX.md` to add the new document link

### Document Structure Reference

```
doc/
├── 00_文档存放规则.md          # Storage rules — READ FIRST before writing docs
├── INDEX.md                     # Master index — update when adding new docs
│
├── 01_architecture/             # Architecture design
├── 02_product/                  # Product design
├── 03_reports/                  # Reports (code reports, audits, reviews)
├── 04_plans/                    # Plans (work plans, roadmaps, todos)
├── 05_meetings/                 # Meeting notes, decisions
├── 06_references/               # Reference materials
└── archive/                     # Archived documents
```

### Priority Markers in Documents

When referencing documents in `INDEX.md`, use emoji to indicate priority:
- 🔴 = High priority — needs immediate attention
- 🟡 = Medium priority — needs attention soon
- 🟢 = Complete — status normal
- 📦 = Archived — historical reference

### Code Documentation Comments

- **Python**: Use docstrings for functions/classes
- **JavaScript**: Use JSDoc style comments
- **Complex logic**: Must add explanatory comments

---

## Before Completing Tasks

Checklist:
- [ ] Code follows naming conventions
- [ ] Functions ≤ 200 lines, files ≤ 800 lines
- [ ] No bare `except` clauses
- [ ] SQL uses parameterized queries
- [ ] Secrets via environment variables only
- [ ] Corresponding test file created
- [ ] Passes `ruff check .`
- [ ] If document created, follows `doc/00_文档存放规则.md`
- [ ] Commit message format: `<type>: <description>`

## Getting Help

- `开发规则.md` — Authoritative rules (Chinese)
- `doc/INDEX.md` — Document index
- `doc/00_文档存放规则.md` — Document storage rules
- `AGENT.md` — General agent development guidelines
