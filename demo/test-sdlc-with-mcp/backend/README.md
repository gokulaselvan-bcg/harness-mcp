# Backend — Tasks API

FastAPI service exposing CRUD operations for tasks. SQLAlchemy 2.x over SQLite,
Alembic for forward-only migrations, pydantic-settings for typed configuration.

All commands below assume you are in the `backend/` directory.

---

## Requirements

- Python 3.11 or newer
- `pip` (a virtual environment is strongly recommended)

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                # adjust if you need non-default ports
alembic upgrade head                # creates tasks.db
```

`tasks.db` is intentionally **not** checked in. The Alembic command above
generates a fresh SQLite file in the current directory.

---

## Running

```bash
uvicorn app.main:app --reload
```

- Service: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Tests

```bash
pytest                              # full suite
pytest -q tests/tasks               # just the tasks feature
pytest --cov=app                    # with coverage
```

Tests cover the service layer and the router layer separately. Coverage on
business logic is 100% by policy.

---

## Configuration

Settings are loaded via `pydantic-settings` from environment variables or a
`.env` file. See [`src/app/settings.py`](src/app/settings.py).

| Variable        | Default                              | Purpose                              |
|-----------------|--------------------------------------|--------------------------------------|
| `DATABASE_URL`  | `sqlite:///./tasks.db`               | SQLAlchemy connection string         |
| `CORS_ORIGINS`  | `["http://localhost:5173"]`          | Allowed frontend origins (JSON list) |

Unknown keys are rejected (`extra="forbid"`) — typos in `.env` fail loud.

---

## API Reference

All endpoints are JSON in, JSON out. Validation errors return HTTP 422 with the
default FastAPI/Pydantic error envelope.

| Method | Path              | Request Body                              | Success | Errors      |
|--------|-------------------|-------------------------------------------|---------|-------------|
| POST   | `/v1/tasks`       | `{title, description?}`                   | 201     | 422         |
| GET    | `/v1/tasks`       | —                                         | 200     | —           |
| PUT    | `/v1/tasks/{id}`  | `{title?, description?, completed?}`      | 200     | 404 / 422   |
| DELETE | `/v1/tasks/{id}`  | —                                         | 204     | 404         |

### Example — create a task

```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Write README", "description": "Backend section"}'
```

### Example — toggle completion

```bash
curl -X PUT http://localhost:8000/v1/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"completed": true}'
```

---

## Project Structure

```
backend/
├── alembic/                # Forward-only migrations
│   ├── env.py
│   └── versions/
│       └── 0001_create_tasks.py
├── alembic.ini
├── pyproject.toml
├── src/
│   └── app/
│       ├── main.py         # FastAPI app instance + CORS + router wiring
│       ├── settings.py     # Pydantic Settings (single source for env)
│       ├── common/
│       │   └── db.py       # SQLAlchemy engine, Base, get_session()
│       └── tasks/          # Feature folder
│           ├── models.py       # ORM model
│           ├── schemas.py      # Pydantic request/response shapes
│           ├── service.py      # Business logic (DB-aware, HTTP-unaware)
│           ├── router.py       # HTTP endpoints
│           └── exceptions.py   # Domain exceptions (TaskNotFound)
└── tests/
    └── tasks/
        ├── conftest.py
        ├── test_router.py
        └── test_service.py
```

---

## Migrations

Migrations are **forward-only** — never edit a committed migration to "fix" it.
Add a new one instead.

```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "describe the change"

# Apply pending migrations
alembic upgrade head

# Show current revision
alembic current
```

---

## Known Deviations

This is a single-user local demo. The following standards from the SDLC
discipline server were intentionally skipped (flagged at plan time):

- **No `tenant_id` / row-level security.** SQLite has no RLS, and this is a
  single-tenant demo.
- **No `Idempotency-Key` on POST.** Demo scope.
- **No CI workflow.** Hooks run locally only.
