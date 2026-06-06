# AI Code Review System

A clean, production-friendly FastAPI backend starter using PostgreSQL, SQLAlchemy ORM, and modular architecture.

## Folder Purpose

- `app/api/routes`: API route modules grouped by feature, such as health checks, users, repositories, or reviews.
- `app/models`: SQLAlchemy ORM models that map Python classes to database tables.
- `app/schemas`: Pydantic request and response schemas used for validation and serialization.
- `app/services`: Business logic layer. Keep route handlers thin by moving real application logic here.
- `app/core`: Application-level configuration, security settings, constants, and shared startup behavior.
- `app/db`: Database setup, sessions, base model metadata, and future migration-related helpers.
- `app/utils`: Small reusable helper functions that do not belong to one specific feature.

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update `DATABASE_URL`.
4. Start the API:

```bash
uvicorn app.main:app --reload
```

5. Open `http://127.0.0.1:8000/docs`.
