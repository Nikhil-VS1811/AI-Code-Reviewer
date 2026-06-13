# AI Code Review System Roadmap

## Current Architecture

The project is a FastAPI backend with a clear feature split:

- API routes handle HTTP concerns for auth, submissions, reviews, and health.
- Services contain authentication, submission ownership checks, review retrieval, and AI review generation.
- SQLAlchemy models store users, code submissions, reviews, and review comments in PostgreSQL.
- Pydantic schemas validate request and response payloads.
- JWT bearer tokens protect submission and review endpoints.
- The AI layer supports a mock provider and an Ollama provider.

## Missing Production Features

- Database migrations with Alembic instead of startup-time table creation.
- Automated tests for auth, ownership boundaries, submission CRUD, review generation, and provider parsing.
- Background review jobs so slow Ollama calls do not block API requests.
- Refresh tokens, token revocation, password reset, and stronger account lifecycle controls.
- OAuth2 social login providers despite OAuth2 password flow already being present.
- Rate limiting, request size limits, and abuse controls for code submission and AI generation.
- Observability beyond basic request logs: structured logs, metrics, traces, and AI latency tracking.
- Deployment assets such as Dockerfile, compose file, environment templates, and CI checks.
- Admin and user-facing review management features such as regeneration, review status, filtering, and pagination.
- Secrets management and production validation for environment-specific settings.

## Production-Grade Roadmap

### Phase 1: Backend Hardening

- Add Alembic migrations and remove direct schema creation from production startup.
- Add pytest coverage with a temporary test database.
- Add pagination, filtering, and consistent error response patterns.
- Add request IDs, CORS settings, readiness checks, and structured logging.

### Phase 2: Review Workflow

- Convert review generation into queued background jobs.
- Track review status: queued, running, completed, failed.
- Add review regeneration and provider failure retry handling.
- Store AI provider metadata, model name, latency, and raw diagnostic errors.

### Phase 3: Authentication and Security

- Add refresh tokens and logout/token revocation.
- Add password reset and email verification.
- Add optional OAuth2 providers such as GitHub or Google.
- Add rate limiting and input size limits.

### Phase 4: Deployment and Operations

- Add Docker and docker-compose for API, PostgreSQL, and Ollama-compatible local development.
- Add CI for formatting, linting, tests, and migration checks.
- Add production configuration guidance and secret handling.
- Add metrics and dashboards for latency, errors, review throughput, and provider health.

### Phase 5: Product Features

- Add repository/project entities so submissions can be grouped by source.
- Add richer review categories, line ranges, severity totals, and trend history.
- Add frontend or API consumers for browsing submissions, reviews, and review status.
- Add team/workspace support and role-based access control.

## Next Development Priority

The next best implementation target is Alembic plus tests. Once schema changes are controlled and core flows are tested, the project can safely move to asynchronous review jobs.
