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
4. Run database migrations:

```bash
alembic upgrade head
```

5. Start the API:

```bash
uvicorn app.main:app --reload
```

6. Open `http://127.0.0.1:8000/docs`.

## Run With Docker

The Docker stack starts PostgreSQL and FastAPI together. Database migrations run
automatically when the API container starts.

```bash
docker compose up --build
```

After startup:

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`
- Readiness check: `http://127.0.0.1:8000/api/v1/ready`

PostgreSQL data is stored in the named Docker volume `postgres_data`, so data
survives container restarts.

Useful Docker commands:

```bash
# Start or rebuild the stack
docker compose up --build

# Run in the background
docker compose up --build -d

# Stop containers without deleting database data
docker compose down

# Stop containers and remove the PostgreSQL volume
docker compose down -v

# Check the current migration revision inside the API container
docker compose exec api python -m alembic current
```

Quick API smoke test after the stack is healthy:

```bash
curl http://127.0.0.1:8000/api/v1/ready

curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"password123"}'

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}' \
  | python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

SUBMISSION_ID=$(curl -s -X POST http://127.0.0.1:8000/submissions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language":"python","code":"def add(a, b):\n    return a + b"}' \
  | python -c "import json,sys; print(json.load(sys.stdin)['id'])")

curl -X POST "http://127.0.0.1:8000/reviews/generate/$SUBMISSION_ID" \
  -H "Authorization: Bearer $TOKEN"
```

The Compose file supports environment overrides through a local `.env` file or
shell environment variables. Important settings include:

```bash
POSTGRES_DB=ai_code_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
API_PORT=8000
DOCKER_APP_ENV=production
DOCKER_DEBUG=false
DOCKER_SECRET_KEY=replace-with-a-long-production-secret
AI_PROVIDER=mock
```

For production, use a strong `SECRET_KEY`, private networking, managed secrets,
and production-specific database credentials. The included Compose file is
intended to be a production-minded local/deployment baseline, not a substitute
for a hardened cloud runtime.

## Frontend

The React frontend lives in `frontend` and is built with Vite, TypeScript,
TailwindCSS, Axios, and React Router.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

By default, the frontend expects the FastAPI backend at
`http://127.0.0.1:8000`. Override it with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Production build:

```bash
cd frontend
npm run build
npm run preview
```

## Database Migrations

This project uses Alembic for PostgreSQL schema management. The application does
not create tables at startup; every schema change must be represented by a
versioned migration in `migrations/versions`.

Common commands:

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back the latest migration
alembic downgrade -1

# Show the current database revision
alembic current

# Create a new migration after changing SQLAlchemy models
alembic revision --autogenerate -m "describe schema change"
```

Migration workflow:

1. Update the SQLAlchemy models in `app/models`.
2. Generate a migration with `alembic revision --autogenerate -m "..."`.
3. Review the generated migration carefully, especially indexes, constraints,
   defaults, data backfills, and downgrade behavior.
4. Test both directions locally with `alembic upgrade head` and
   `alembic downgrade -1`.
5. Commit the model changes and migration together.

For production deployments, run `alembic upgrade head` as a release step before
starting the new application version. Avoid editing old migration files after
they have been shared or deployed; create a new migration instead.
