# Task Manager Backend

FastAPI + SQLite CRUD API.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/uvicorn app.main:app --reload
```

Server runs at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Test

```bash
.venv/bin/pytest
```

## Endpoints

| Method | Path           | Description       |
|--------|----------------|-------------------|
| POST   | /tasks         | Create a task     |
| GET    | /tasks         | List all tasks    |
| GET    | /tasks/{id}    | Read one task     |
| PUT    | /tasks/{id}    | Update a task     |
| DELETE | /tasks/{id}    | Delete a task     |
