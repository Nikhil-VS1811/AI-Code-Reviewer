# AI Code Review System

![CI Pipeline](https://github.com/Nikhil-VS1811/AI-Code-Reviewer/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3.1-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7.2-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**AI Code Review System** is a full-stack code quality and security review platform built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, and **React + TypeScript**. It addresses a common developer workflow gap: catching high-risk security patterns (command injection, arbitrary code execution, unsafe deserialization, XSS sinks, and C buffer overflows) before merge while pairing deterministic static analysis with structured AI review feedback, historical quality tracking, public GitHub repository scanning, and downloadable PDF audit reports.

---

## Table of Contents

1. [Live Demo and Links](#1-live-demo-and-links)
2. [Existing Screenshots & Sample Reports](#2-existing-screenshots--sample-reports)
3. [Key Features](#3-key-features)
4. [Technology Stack](#4-technology-stack)
5. [Architecture](#5-architecture)
6. [How Code Review Works](#6-how-code-review-works)
7. [Static Security Analysis](#7-static-security-analysis)
8. [AI Integration](#8-ai-integration)
9. [API Overview](#9-api-overview)
10. [Database Design](#10-database-design)
11. [Project Structure](#11-project-structure)
12. [Local Setup and Installation](#12-local-setup-and-installation)
13. [Environment Variables](#13-environment-variables)
14. [Docker Setup](#14-docker-setup)
15. [Testing and Quality Checks](#15-testing-and-quality-checks)
16. [Deployment](#16-deployment)
17. [Security Measures](#17-security-measures)
18. [Current Limitations](#18-current-limitations)
19. [Roadmap / Future Improvements](#19-roadmap--future-improvements)
20. [Contributing](#20-contributing)
21. [License](#21-license)

---

## 1. Live Demo and Links

| Resource | URL | Description |
| :--- | :--- | :--- |
| **Frontend Application** | [https://ai-code-reviewer-seven-brown.vercel.app/](https://ai-code-reviewer-seven-brown.vercel.app/) | Production React SPA deployed on Vercel |
| **Interactive Guest Demo** | [https://ai-code-reviewer-seven-brown.vercel.app/demo](https://ai-code-reviewer-seven-brown.vercel.app/demo) | Public read-only walkthrough — **no registration or login required** |
| **API Documentation (Swagger UI)** | [https://ai-code-reviewer-api-wgz8.onrender.com/docs](https://ai-code-reviewer-api-wgz8.onrender.com/docs) | Interactive OpenAPI 3.1 documentation hosted on Render |
| **Backend Health Probe** | [https://ai-code-reviewer-api-wgz8.onrender.com/api/v1/health](https://ai-code-reviewer-api-wgz8.onrender.com/api/v1/health) | Liveness check (`{"status": "ok", ...}`) |
| **Backend Readiness Probe** | [https://ai-code-reviewer-api-wgz8.onrender.com/api/v1/ready](https://ai-code-reviewer-api-wgz8.onrender.com/api/v1/ready) | Executes `SELECT 1` against PostgreSQL (`{"status": "ok", "checks": {"database": "ok"}}`) |
| **GitHub Repository** | [https://github.com/Nikhil-VS1811/AI-Code-Reviewer](https://github.com/Nikhil-VS1811/AI-Code-Reviewer) | Source code, CI pipeline, migrations, and test suites |

> **Important Note on the Guest Demo (`/demo`):**
> The [`/demo`](https://ai-code-reviewer-seven-brown.vercel.app/demo) route ([`GuestDemoPage.tsx`](frontend/src/pages/GuestDemoPage.tsx)) is strictly isolated from protected backend APIs and renders predefined, static sample scenarios from [`frontend/src/data/guestDemoData.ts`](frontend/src/data/guestDemoData.ts). It exists so visitors and recruiters can inspect the scoring layout, severity breakdowns, and remediation UI immediately without creating an account. **Sample output shown on `/demo` is not a live AI or static scan.** To run live code submissions or GitHub repository scans, create an account on [`/signup`](https://ai-code-reviewer-seven-brown.vercel.app/signup).

---

## 2. Existing Screenshots & Sample Reports

### Landing Page
Overview of platform capabilities, direct entry to the interactive Guest Demo (`/demo`), and authentication links.
![Landing Page](Screenshots/landing-page.png)

### Authentication (Login & Registration)
JWT-backed registration and login flows with client- and server-side email normalization.
![Login Page](Screenshots/login.png)
![Registration Page](Screenshots/register.png)

### Analytics Dashboard
Visualizes aggregate quality scores, submission counts, and severity distributions using Recharts.
![Dashboard](Screenshots/dashboard.png)

### Code Review Results & Review History
Detailed multi-score breakdown (`Overall`, `Security`, `Performance`, `Maintainability`, `Readability`), executive summary, line-level findings, and historical review browser.
![Code Review Results](Screenshots/code-review.png)
![Review History Page](Screenshots/review-page.png)

### GitHub Repository Security Review
Repository-level vulnerability scanner displaying `Repository Health Score`, severity counters (`Critical`, `High`, `Medium`, `Low`), file-level findings, strengths, weaknesses, and remediation recommendations.
![Repository Review](Screenshots/repository-review.png)

### Sample Generated PDF Reports
The repository includes two real PDF reports generated by the backend's pure-Python PDF builders:
- [Sample Code Review Report (`docs/sample-code-review-report.pdf`)](docs/sample-code-review-report.pdf)
- [Sample Repository Review Report (`docs/sample-repository-review-report.pdf`)](docs/sample-repository-review-report.pdf)

---

## 3. Key Features

- **Code Submission with Monaco Editor (`/submit`):** Authenticated users submit code snippets (`1` to `100,000` characters) with language selection (`python`, `javascript`, `typescript`, `java`, `cpp`, etc.) via an embedded Monaco Editor ([`SubmitCodePage.tsx`](frontend/src/pages/SubmitCodePage.tsx)).
- **Hybrid Static + AI Code Review (`/reviews/generate/{submission_id}`):** Combines deterministic regex security scanning ([`scan_code()`](app/services/security/static_scanner.py)) with structured AI evaluation ([`AIReviewService`](app/services/ai_review_service.py)) to produce five integer scores (`0–100`), a summary, and line-level comments (`line_number`, `severity`, `category`, `comment`).
- **Automated Security Score Penalties:** Static security findings are appended to the review's comment list and deterministically penalize the review's `security_score` (`-20` per `critical` finding, `-10` per `high` finding) and `overall_score` (`-10` per `critical`, `-5` per `high`), clamped to `[0, 100]`.
- **Public GitHub Repository Scanner (`/repository-review`):** Clones any public `https://github.com/<owner>/<repo>` repository with `git clone --depth 1`, scans up to `500` source files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.h`, max `500 KB` each) within a `30-second` scan deadline, and returns a `0–100` `repository_health_score`, severity counts, strengths, weaknesses, and actionable recommendations.
- **Comment- & Docstring-Aware Static Analysis:** [`mask_inert_code()`](app/services/security/static_scanner.py) strips inline comments (`#`, `//`), block comments (`/* ... */`), and Python triple-quoted docstrings (`"""..."""`, `'''...'''`) into newline-preserving whitespace before applying security rules, eliminating false positives from comments while preserving exact line numbers.
- **Zero-Dependency PDF Report Generation:** Pure-Python PDF 1.4 stream builders ([`pdf_report_service.py`](app/services/pdf_report_service.py) and [`repository_pdf_service.py`](app/services/repository_pdf_service.py)) export single-submission reviews (`/reviews/{review_id}/pdf`) and repository scan reports (`/repository-review/export-pdf`) without external system binaries.
- **Paginated History & Ownership Isolation:** `GET /submissions` and `GET /reviews` enforce strict per-user ownership (`Submission.user_id == current_user.id`) and support `limit` (`1–100`, default `20`) and `offset` (`>= 0`, default `0`) pagination.
- **Theme-Aware Responsive UI & Guest Demo:** Supports dark/light theme toggling ([`ThemeContext.tsx`](frontend/src/contexts/ThemeContext.tsx)), protected route guards ([`ProtectedRoute.tsx`](frontend/src/routes/ProtectedRoute.tsx)), and an unauthenticated `/demo` showcase.

---

## 4. Technology Stack

| Category | Technology | Version | Purpose in This Project |
| :--- | :--- | :--- | :--- |
| **Frontend** | React & React DOM | `18.3.1` | Component UI rendering and state management (`AuthContext`, `ThemeContext`) |
| **Frontend** | TypeScript | `5.7.2` | Static typing across API payloads, components, and contexts |
| **Frontend** | Vite (`@vitejs/plugin-react`) | `6.0.6` | Frontend dev server and production bundler |
| **Frontend** | React Router DOM | `6.28.2` | Client-side routing (`/`, `/demo`, `/login`, `/signup`, protected dashboard routes) |
| **Frontend** | Tailwind CSS, PostCSS, Autoprefixer | `3.4.17` | Utility-first styling and dark/light mode design system |
| **Frontend** | `@monaco-editor/react` | `^4.7.0` | VS Code-powered code editor on `/submit` |
| **Frontend** | Recharts | `^3.8.1` | Score and severity visualization charts on `/dashboard` |
| **Frontend** | Axios | `1.7.9` | HTTP client with automatic `Authorization: Bearer <token>` header injection |
| **Frontend** | Lucide React | `0.468.0` | UI iconography |
| **Backend & API** | Python | `3.12` | Core backend runtime (verified on Python `3.12` in Docker/CI and `3.14` locally) |
| **Backend & API** | FastAPI | `0.115.6` | REST API framework, dependency injection, and OpenAPI 3.1 schema generation |
| **Backend & API** | Pydantic & `pydantic-settings` | `2.x` / `2.7.0` | Request/response validation, score clamping, and `.env` configuration parsing |
| **Backend & API** | Uvicorn (`uvicorn[standard]`) | `0.34.0` | ASGI server running the FastAPI application |
| **Backend & API** | `email-validator` & `python-multipart` | `2.2.0` / `0.0.20` | `EmailStr` validation and OAuth2 form-data login parsing |
| **AI / LLM Integration** | `OllamaReviewProvider` (`urllib.request`) | Custom | Calls local Ollama `POST /api/generate` (`format: "json"`, `temperature: 0`) with retries |
| **AI / LLM Integration** | `MockAIReviewProvider` | Built-in | Deterministic JSON review generator used by default (`AI_PROVIDER=mock`) |
| **Static Analysis & Security** | `static_scanner.py` & `github_service.py` | Built-in | Comment-masking lexer, 14 multi-language regex security rules, hardened `git clone` |
| **Database & Migrations** | PostgreSQL | `16` | Primary relational database (Neon in production, `postgres:16-alpine` in Docker) |
| **Database & Migrations** | SQLAlchemy | `2.0.36` | ORM models (`Mapped`/`mapped_column`), relationships, and query construction |
| **Database & Migrations** | `psycopg[binary]` | `3.3.4` | PostgreSQL v3 driver (`postgresql+psycopg://`) |
| **Database & Migrations** | Alembic | `1.14.0` | Schema migrations (`0001_initial_schema`, `0002_case_insensitive_email`) |
| **Authentication** | `python-jose[cryptography]` | `3.3.0` | `HS256` JWT creation and verification (`OAuth2PasswordBearer`) |
| **Authentication** | `passlib[bcrypt]` & `bcrypt` | `1.7.4` / `4.0.1` | Salted `bcrypt` password hashing and verification |
| **Testing & Quality** | Python `unittest` | Stdlib | 43 backend unit and regression tests across 7 test modules in [`tests/`](tests/) |
| **Testing & Quality** | Node.js Test Runner (`node --test`) | Node `20+` | 6 frontend SSR/isolation/routing tests in [`frontend/tests/guest_demo.test.mjs`](frontend/tests/guest_demo.test.mjs) |
| **Testing & Quality** | ESLint & `typescript-eslint` | `9.17.0` / `8.19.0` | Frontend TypeScript and React Hooks linting |
| **DevOps & Deployment** | Docker, Docker Compose, GitHub Actions, Vercel, Render | — | Containerization, automated CI pipeline, SPA hosting, and Dockerized API hosting |

---

## 5. Architecture

The system follows a layered architecture separating HTTP routing, rate limiting, business services, static/AI analyzers, and database persistence:

- **Client Layer (`frontend/src/`):** React SPA communicating with the backend via [`frontend/src/api/client.ts`](frontend/src/api/client.ts). Public routes (`/`, `/demo`, `/login`, `/signup`) are accessible without a token; application routes (`/dashboard`, `/submit`, `/reviews`, `/reviews/:reviewId`, `/repository-review`) are wrapped in [`ProtectedRoute`](frontend/src/routes/ProtectedRoute.tsx) and [`AppShell`](frontend/src/components/AppShell.tsx).
- **Middleware & Cross-Cutting Layer (`app/main.py`, `app/core/rate_limit.py`):**
  - [`RequestContextMiddleware`](app/main.py) attaches an `X-Request-ID` header and logs request method, path, status code, and latency in milliseconds.
  - `CORSMiddleware` restricts cross-origin requests to explicit origins (`http://localhost:5173`, `https://ai-code-reviewer-seven-brown.vercel.app`, plus non-wildcard entries from `CORS_ORIGINS`).
  - [`RateLimiter`](app/core/rate_limit.py) enforces per-user sliding-window limits on review generation and repository scanning.
- **Service & Analysis Layer (`app/services/`):** Encapsulates user authentication, submission CRUD, hybrid review orchestration, pluggable AI providers, shallow Git cloning, static scanning, and PDF generation.
- **Persistence Layer (`app/db/`, `app/models/`, `migrations/`):** SQLAlchemy 2.0 session management (`pool_pre_ping=True`) and Alembic migrations targeting PostgreSQL.

```mermaid
flowchart TD
    subgraph Client["Frontend SPA (React 18 + TypeScript + Vite on Vercel)"]
        LP["Landing Page (/)"]
        GD["Guest Demo (/demo - Local Sample Data Only)"]
        AUTH_UI["Login & Signup (/login, /signup)"]
        DASH_UI["Protected App (/dashboard, /submit, /reviews, /repository-review)"]
    end

    subgraph API["FastAPI Backend (Render Docker Runtime)"]
        MW["Middleware (RequestContextMiddleware + CORSMiddleware)"]
        RL["Per-User RateLimiter (In-Memory Sliding Window)"]
        AUTH_R["Auth Router (/auth)"]
        SUB_R["Submissions Router (/submissions)"]
        REV_R["Reviews Router (/reviews)"]
        REPO_R["Repository Review Router (/repository-review)"]
        HLTH_R["Health Router (/api/v1/health, /api/v1/ready)"]
    end

    subgraph Services["Domain & Analysis Services"]
        AUTH_S["auth_service (JWT HS256 + bcrypt + lower(email))"]
        REV_GEN["review_generation_service (Orchestrator + Penalty Logic)"]
        AI_S["ai_review_service (MockAIReviewProvider / OllamaReviewProvider)"]
        SCAN_S["static_scanner (mask_inert_code + 14 Regex Rules)"]
        REPO_S["repository_review_service + repository_scanner"]
        GIT_S["github_service (Validated HTTPS Shallow Clone + Cleanup)"]
        PDF_S["pdf_report_service & repository_pdf_service"]
    end

    subgraph External["Persistence & External Dependencies"]
        PG[("PostgreSQL (users, submissions, reviews, review_comments)")]
        GH["Public GitHub Repos (https://github.com/owner/repo)"]
        OLLAMA["Local Ollama API (Optional: POST /api/generate)"]
    end

    LP --> GD
    LP --> AUTH_UI
    AUTH_UI --> MW
    DASH_UI --> MW
    MW --> AUTH_R
    MW --> SUB_R
    MW --> REV_R
    MW --> REPO_R
    MW --> HLTH_R
    REV_R --> RL
    REPO_R --> RL
    AUTH_R --> AUTH_S
    AUTH_S --> PG
    HLTH_R --> PG
    SUB_R --> PG
    REV_R --> REV_GEN
    REV_R --> PDF_S
    REV_GEN --> SCAN_S
    REV_GEN --> AI_S
    REV_GEN --> PG
    AI_S -. "When AI_PROVIDER=ollama" .-> OLLAMA
    REPO_R --> REPO_S
    REPO_R --> PDF_S
    REPO_S --> GIT_S
    REPO_S --> SCAN_S
    GIT_S --> GH
```

---

## 6. How Code Review Works

### A. Single Code Submission Pipeline
1. **Submission (`POST /submissions`):** The authenticated user submits `language` (`1–50` chars, normalized to lowercase) and `code` (`1–100,000` chars, must not be whitespace-only). The snippet is stored in the `submissions` table linked to `current_user.id`.
2. **Review Trigger (`POST /reviews/generate/{submission_id}`):**
   - [`review_generation_rate_limiter`](app/core/rate_limit.py) verifies the user has not exceeded `10` review generations in the last `60` seconds.
   - [`generate_review_for_submission()`](app/services/review_generation_service.py) verifies the submission belongs to `current_user` and that no review already exists for `submission_id` (returning `409 Conflict` if one already exists).
3. **Static Scan + AI Review Execution:**
   - [`scan_code(submission.code)`](app/services/security/static_scanner.py) masks comments/docstrings and evaluates all 14 regex security rules, returning line-numbered `critical` and `high` findings.
   - [`AIReviewService.review_code()`](app/services/ai_review_service.py) builds a structured prompt and invokes the active provider (`MockAIReviewProvider` or `OllamaReviewProvider`), parsing and clamping all five scores into `[0, 100]` via [`AIReviewResult`](app/services/ai_review_service.py).
4. **Score Penalty & Persistence:**
   - Static findings are appended to `ai_review.comments`.
   - A deterministic penalty is calculated: `penalty = (critical_count * 20) + (high_count * 10)`.
   - `security_score = max(0, security_score - penalty)` and `overall_score = max(0, overall_score - penalty // 2)`.
   - The `Review` and its `ReviewComment` rows are committed atomically to PostgreSQL.
5. **PDF Export (`GET /reviews/{review_id}/pdf`):** [`generate_review_pdf()`](app/services/pdf_report_service.py) renders the scores, summary, and line-level comments into a downloadable `review-<id>.pdf` document.

### B. GitHub Repository Review Pipeline
1. **Request & Rate Limit (`POST /repository-review` or `/repository-review/export-pdf`):** Requires a valid JWT and passes through [`repository_scan_rate_limiter`](app/core/rate_limit.py) (`5` requests per `60` seconds per user).
2. **URL Validation & Hardened Shallow Clone:** [`validate_github_url()`](app/services/github_service.py) enforces `^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$`, rejects leading hyphens and `.`/`..` segments, and runs `git clone --depth 1 -- <canonical_url> <temp_dir>` with a `60s` timeout, `GIT_TERMINAL_PROMPT=0`, and HTTPS-only Git protocol restrictions.
3. **File Collection & Static Scanning:** [`collect_source_files()`](app/services/repository_scanner.py) walks the tree (skipping `.git`, `node_modules`, `dist`, `build`, `coverage`, `venv`, `.venv`, `__pycache__`) and collects up to `500` files matching `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.h` (`<= 500 KB` each) within a `30s` deadline. Each file is scanned with [`scan_code()`](app/services/security/static_scanner.py).
4. **Health Scoring & Guaranteed Cleanup:** [`_build_repository_summary()`](app/services/repository_review_service.py) computes `repository_health_score = clamp(100 - 10*critical - 5*high - 2*medium - low, 0, 100)` along with up to 5 strengths, 5 weaknesses, and 5 recommendations. The temporary clone directory is always deleted in `finally: cleanup_repository(repo_path)`.

---

## 7. Static Security Analysis

Implemented in [`app/services/security/static_scanner.py`](app/services/security/static_scanner.py), the static scanner operates in two stages:

1. **Inert Code Masking (`mask_inert_code`):**
   - Replaces C/JS block comments (`/* ... */`) and Python triple-quoted strings/docstrings (`"""..."""`, `'''...'''`) with spaces while preserving `\n` characters so line numbers never shift.
   - Walks each line character-by-character, tracking single/double-quoted string literals (`'` and `"`) and backslash escapes (`\`), and strips trailing `#` or `//` comments outside string literals.
2. **Pattern Matching (`SECURITY_RULES`):**
   Evaluates 14 regular-expression rules against each masked line:

| Ecosystem | Rule Pattern | Severity | Category | Message |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | `\beval\s*\(` | `critical` | `security` | `Use of eval() detected.` |
| **Python** | `\bexec\s*\(` | `critical` | `security` | `Use of exec() detected.` |
| **Python** | `\bpickle\.loads\s*\(` | `high` | `security` | `pickle.loads() may execute arbitrary code.` |
| **Python** | `\bos\.system\s*\(` | `high` | `security` | `os.system() command execution detected.` |
| **Python** | `\bshell\s*=\s*True` | `critical` | `security` | `subprocess shell=True detected.` |
| **JS / TS** | `\binnerHTML\b` | `high` | `security` | `innerHTML may cause XSS vulnerabilities.` |
| **JS / TS** | `\bnew\s+Function\s*\(` | `critical` | `security` | `new Function() detected.` |
| **JS / TS** | `\bdocument\.write\s*\(` | `high` | `security` | `document.write() detected.` |
| **Java** | `\bRuntime\.getRuntime\s*\(\)\.exec\s*\(` | `critical` | `security` | `Runtime.exec() detected.` |
| **Java** | `\bProcessBuilder\s*\(` | `high` | `security` | `ProcessBuilder execution detected.` |
| **C / C++** | `(?<![\.\w])system\s*\(` | `critical` | `security` | `system() call detected.` |
| **C / C++** | `(?<![\.\w])popen\s*\(` | `high` | `security` | `popen() detected.` |
| **C / C++** | `\bgets\s*\(` | `critical` | `security` | `Unsafe gets() usage detected.` |
| **C / C++** | `\bstrcpy\s*\(` | `high` | `security` | `strcpy() may cause buffer overflows.` |

---

## 8. AI Integration

Configured via `AI_PROVIDER` in [`app/core/config.py`](app/core/config.py) and dispatched by [`get_ai_review_provider()`](app/services/ai_review_service.py):

### 1. `AI_PROVIDER=mock` (Default)
- Uses [`MockAIReviewProvider`](app/services/ai_review_service.py), which returns a deterministic, schema-valid JSON review (`overall_score: 82`, `security_score: 78`, `performance_score: 84`, `maintainability_score: 80`, `readability_score: 86`, plus 4 baseline review comments) that is then combined with real findings and score penalties from `scan_code()`.
- Requires zero external API keys or GPU hardware, making it suitable for cloud free-tier deployments and automated CI tests.

### 2. `AI_PROVIDER=ollama` (Local LLM Inference)
- Uses [`OllamaReviewProvider`](app/services/providers/ollama_provider.py) to send a `POST {OLLAMA_BASE_URL}/api/generate` request with `"stream": false`, `"format": "json"`, and `"temperature": 0`.
- **Supported Models (`SUPPORTED_OLLAMA_MODELS`):**
  - `qwen3:4b` (default)
  - `qwen2.5-coder:7b`
  - `llama3.1:8b`
  - `gemma4:12b`
  *(Any model tag outside this allowlist raises a `ValueError` at initialization.)*
- **Resilience & Validation:** Retries transient `TimeoutError` / `URLError` failures up to `max_retries=2` times (`retry_delay_seconds=1.0`), normalizes numeric/string scores into `[0, 100]` via [`normalize_review_scores()`](app/services/ai_review_service.py), and validates the response against [`AIReviewResult`](app/services/ai_review_service.py). Malformed JSON or schema mismatches return `HTTP 502 Bad Gateway`; timeouts return `HTTP 504 Gateway Timeout`.

---

## 9. API Overview

Interactive Swagger UI documentation is available at [`https://ai-code-reviewer-api-wgz8.onrender.com/docs`](https://ai-code-reviewer-api-wgz8.onrender.com/docs) (and `http://localhost:8000/docs` locally).

| Method | Endpoint | Auth | Rate Limit | Summary & Key Parameters |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Public | — | Register a new user (`username` `3–50` chars, `email`, `password` `8–72` chars). Returns `201 Created` (`UserResponse`). |
| `POST` | `/auth/login` | Public | — | OAuth2 form-urlencoded login (`username` = email, `password`). Returns `Token` (`access_token`, `token_type: "bearer"`). |
| `POST` | `/auth/login/json` | Public | — | JSON login (`email`, `password`). Returns `Token`. |
| `GET` | `/auth/me` | Bearer JWT | — | Return the currently authenticated `UserResponse`. |
| `POST` | `/submissions` | Bearer JWT | — | Create a code submission (`language` `1–50` chars, `code` `1–100,000` chars). Returns `201 Created`. |
| `GET` | `/submissions` | Bearer JWT | — | List current user's submissions (`limit` `1–100`, default `20`; `offset >= 0`, default `0`). |
| `GET` | `/submissions/{submission_id}` | Bearer JWT | — | Fetch a single submission owned by the current user (`404` if not found/owned). |
| `DELETE` | `/submissions/{submission_id}` | Bearer JWT | — | Delete an owned submission and cascade-delete its review (`204 No Content`). |
| `POST` | `/reviews/generate/{submission_id}` | Bearer JWT | `10 req / 60s` | Run static + AI analysis for an owned submission and persist the review (`409` if review already exists). |
| `GET` | `/reviews` | Bearer JWT | — | List current user's generated reviews with comments (`limit` `1–100`, default `20`; `offset >= 0`, default `0`). |
| `GET` | `/reviews/{review_id}` | Bearer JWT | — | Fetch a single review with comments owned by the current user. |
| `GET` | `/reviews/{review_id}/pdf` | Bearer JWT | — | Download a formatted PDF report (`review-{review_id}.pdf`) for an owned review. |
| `POST` | `/repository-review` (and `/repository-review/`) | Bearer JWT | `5 req / 60s` | Clone and scan a public HTTPS GitHub repository (`repo_url`). Returns health score, severity counts, and findings. |
| `POST` | `/repository-review/export-pdf` | Bearer JWT | `5 req / 60s` | Scan a public HTTPS GitHub repository and stream `repository-report.pdf` (`application/pdf`). |
| `GET` | `/api/v1/health` | Public | — | Liveness check (`200 OK`). |
| `GET` | `/api/v1/ready` | Public | — | Database readiness check (`200 OK` if `SELECT 1` succeeds, `503` otherwise). |

---

## 10. Database Design

Defined using SQLAlchemy 2.0 declarative models in [`app/models/`](app/models/) and managed via Alembic in [`migrations/versions/`](migrations/versions/):

| Table | Model | Key Columns & Constraints | Relationships & Cascades |
| :--- | :--- | :--- | :--- |
| `users` | [`User`](app/models/user.py) | `id` (PK), `username` (`VARCHAR(50)`, indexed), `email` (`VARCHAR(255)`, unique, indexed + unique expression index `ix_users_lower_email` on `lower(email)`), `hashed_password` (`VARCHAR(255)`), `created_at` (`TIMESTAMPTZ`) | One-to-many with `submissions` (`cascade="all, delete-orphan"`) |
| `submissions` | [`Submission`](app/models/submission.py) | `id` (PK), `user_id` (`FK -> users.id ON DELETE CASCADE`, indexed), `language` (`VARCHAR(50)`, indexed), `code` (`TEXT`), `created_at` (`TIMESTAMPTZ`) | Many-to-one with `users`; one-to-one with `reviews` (`uselist=False`, `cascade="all, delete-orphan"`) |
| `reviews` | [`Review`](app/models/review.py) | `id` (PK), `submission_id` (`FK -> submissions.id ON DELETE CASCADE`, `UNIQUE`, indexed), `overall_score`, `security_score`, `performance_score`, `maintainability_score`, `readability_score` (`INTEGER`), `summary` (`TEXT`), `created_at` (`TIMESTAMPTZ`) | One-to-one with `submissions`; one-to-many with `review_comments` (`cascade="all, delete-orphan"`) |
| `review_comments` | [`ReviewComment`](app/models/review.py) | `id` (PK), `review_id` (`FK -> reviews.id ON DELETE CASCADE`, indexed), `line_number` (`INTEGER`), `severity` (`VARCHAR(50)`, indexed), `category` (`VARCHAR(100)`, indexed), `comment` (`TEXT`) | Many-to-one with `reviews` |

### Alembic Migration History
1. **[`2026_06_06_0001_initial_schema.py`](migrations/versions/2026_06_06_0001_initial_schema.py):** Creates `users`, `submissions`, `reviews`, and `review_comments` tables and standard indexes.
2. **[`2026_10_11_0002_case_insensitive_email.py`](migrations/versions/2026_10_11_0002_case_insensitive_email.py):**
   - Queries `SELECT COUNT(*) FROM (SELECT 1 FROM users GROUP BY lower(email) HAVING COUNT(*) > 1) AS duplicate_groups`.
   - Raises a PII-free `RuntimeError` if any duplicate case-insensitive email group exists (preventing partial migrations).
   - Normalizes existing rows via `UPDATE users SET email = lower(email) WHERE email != lower(email)` and creates the unique functional index `ix_users_lower_email` on `lower(email)`.

---

## 11. Project Structure

```text
AI-Code-Reviewer/
├── .github/
│   └── workflows/
│       └── ci.yml                                     # GitHub Actions CI (frontend, backend, docker jobs)
├── Screenshots/                                       # Verified UI screenshots used in README
│   ├── code-review.png
│   ├── dashboard.png
│   ├── landing-page.png
│   ├── login.png
│   ├── register.png
│   ├── repository-review.png
│   └── review-page.png
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py                                # /auth/signup, /auth/login, /auth/login/json, /auth/me
│   │       ├── health.py                              # /api/v1/health, /api/v1/ready
│   │       ├── repository_review.py                   # /repository-review, /repository-review/export-pdf
│   │       ├── reviews.py                             # /reviews/generate/{id}, /reviews, /reviews/{id}/pdf
│   │       └── submissions.py                         # /submissions CRUD & pagination
│   ├── core/
│   │   ├── config.py                                  # Pydantic Settings & environment validation
│   │   └── rate_limit.py                              # Thread-safe per-user sliding-window RateLimiter
│   ├── db/
│   │   ├── base.py
│   │   ├── base_class.py                              # SQLAlchemy DeclarativeBase
│   │   └── database.py                                # Engine (pool_pre_ping=True) & get_db dependency
│   ├── models/
│   │   ├── review.py                                  # Review & ReviewComment ORM models
│   │   ├── submission.py                              # Submission ORM model
│   │   └── user.py                                    # User ORM model
│   ├── schemas/
│   │   ├── health.py
│   │   ├── repository_review.py                       # RepositoryReviewRequest (max_length=512)
│   │   ├── review.py
│   │   ├── submission.py                              # SubmissionCreate (MAX_SUBMISSION_CODE_LENGTH=100,000)
│   │   └── user.py                                    # UserCreate, UserLogin, UserResponse, Token
│   ├── services/
│   │   ├── providers/
│   │   │   └── ollama_provider.py                     # OllamaReviewProvider (/api/generate JSON client)
│   │   ├── security/
│   │   │   └── static_scanner.py                      # mask_inert_code() + 14 SECURITY_RULES
│   │   ├── ai_review_service.py                       # AIReviewService, MockAIReviewProvider, score clamping
│   │   ├── auth_service.py                            # bcrypt hashing, JWT creation, case-insensitive lookup
│   │   ├── github_service.py                          # URL regex validation & hardened shallow git clone
│   │   ├── pdf_report_service.py                      # Pure-Python PDF builder for code reviews
│   │   ├── repository_pdf_service.py                  # Pure-Python PDF builder for repository reports
│   │   ├── repository_review_service.py               # Repository scan orchestration & health score
│   │   ├── repository_scanner.py                      # Bounded file collector (500 files, 500 KB, 30s)
│   │   ├── review_generation_service.py               # Hybrid static + AI review orchestrator
│   │   ├── review_service.py                          # Paginated review queries
│   │   └── submission_service.py                      # Paginated submission queries & deletion
│   └── main.py                                        # FastAPI app factory, CORS, RequestContextMiddleware
├── docs/
│   ├── sample-code-review-report.pdf                  # Sample single-submission PDF report
│   └── sample-repository-review-report.pdf            # Sample repository security PDF report
├── frontend/
│   ├── src/
│   │   ├── api/                                       # Axios client & endpoint wrappers
│   │   ├── components/                                # AppShell, MetricCard, ScoreBadge, EmptyState, etc.
│   │   ├── contexts/                                  # AuthContext.tsx, ThemeContext.tsx
│   │   ├── data/
│   │   │   └── guestDemoData.ts                       # Static sample data for /demo
│   │   ├── pages/                                     # Landing, GuestDemo, Login, Signup, Dashboard, etc.
│   │   ├── routes/
│   │   │   └── ProtectedRoute.tsx                     # JWT route guard
│   │   ├── types/                                     # TypeScript interfaces
│   │   ├── App.tsx                                    # Route definitions
│   │   └── main.tsx                                   # React DOM root
│   ├── tests/
│   │   └── guest_demo.test.mjs                        # Node --test suite for /demo & Vercel SPA config
│   ├── Dockerfile                                     # Node 20-alpine dev container
│   ├── package.json
│   ├── vercel.json                                    # SPA rewrite (/(.*) -> /index.html)
│   └── vite.config.ts
├── migrations/
│   ├── versions/
│   │   ├── 2026_06_06_0001_initial_schema.py
│   │   └── 2026_10_11_0002_case_insensitive_email.py
│   └── env.py
├── scripts/
│   └── start.sh                                       # Runs `python -m alembic upgrade head` then `uvicorn`
├── tests/                                             # 43 backend unittest tests across 7 modules
│   ├── test_cors_config.py
│   ├── test_email_normalization.py
│   ├── test_github_service.py
│   ├── test_pagination.py
│   ├── test_repository_review_route.py
│   ├── test_repository_scanner.py
│   └── test_scanner_accuracy.py
├── .env.example                                       # Sanitized environment variable template
├── Dockerfile                                         # Production Python 3.12-slim backend image
├── LICENSE                                            # MIT License
├── alembic.ini
├── docker-compose.yml                                 # 3-service local stack (db, api, frontend)
└── requirements.txt                                   # Pinned backend Python dependencies
```

---

## 12. Local Setup and Installation

### Prerequisites
- **Python** `3.12+`
- **Node.js** `20+` and **npm**
- **PostgreSQL** `14+` (running locally or accessible via connection URL)
- **Git** (required on `PATH` for repository scanning)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Nikhil-VS1811/AI-Code-Reviewer.git
cd AI-Code-Reviewer
```

### Step 2: Set Up the Python Virtual Environment & Backend Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy [`.env.example`](.env.example) to `.env` and update `DATABASE_URL` and `SECRET_KEY` (must be at least 32 characters):
```bash
cp .env.example .env
```

### Step 4: Create the PostgreSQL Database & Run Alembic Migrations
Ensure your local PostgreSQL instance has a database named `ai_code_review` (matching `DATABASE_URL` in `.env`), then apply all migrations:
```bash
alembic upgrade head
```

### Step 5: Start the FastAPI Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API base URL: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### Step 6: Install Frontend Dependencies & Start Vite Dev Server
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
- Frontend URL: `http://localhost:5173`
- By default, [`frontend/src/api/client.ts`](frontend/src/api/client.ts) sends API requests to `VITE_API_BASE_URL` or falls back to `http://localhost:8000`.

---

## 13. Environment Variables

All backend settings are validated at startup by [`Settings`](app/core/config.py) using [`.env.example`](.env.example) as the template:

```env
APP_NAME="AI Code Review System"
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_code_review

SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

AI_PROVIDER=mock
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT_SECONDS=60
# OLLAMA_MODEL=qwen2.5-coder:7b

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

| Variable | Layer | Required | Default | Validation & Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `APP_NAME` | Backend | No | `"AI Code Review System"` | FastAPI title in OpenAPI docs |
| `APP_ENV` | Backend | No | `"development"` | When set to `"production"`, rejects the default placeholder `SECRET_KEY` |
| `DEBUG` | Backend | No | `False` | FastAPI debug mode flag |
| `DATABASE_URL` | Backend | **Yes** | — | SQLAlchemy connection string (e.g., `postgresql+psycopg://user:pass@host:5432/dbname`) |
| `SECRET_KEY` | Backend | **Yes** | `"change-this-secret-key-in-production"` | JWT signing key; any custom value must be **at least 32 characters** (`validate_secret_key`) |
| `ALGORITHM` | Backend | No | `"HS256"` | JWT signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | No | `30` | JWT expiration window in minutes |
| `AI_PROVIDER` | Backend | No | `"mock"` | Must be `"mock"` or `"ollama"` (case-insensitive) |
| `OLLAMA_MODEL` | Backend | No | `"qwen3:4b"` | Allowed values: `qwen3:4b`, `qwen2.5-coder:7b`, `llama3.1:8b`, `gemma4:12b` |
| `OLLAMA_BASE_URL` | Backend | No | `"http://localhost:11434"` | Base URL for Ollama HTTP requests when `AI_PROVIDER=ollama` |
| `OLLAMA_TIMEOUT_SECONDS` | Backend | No | `60` | Per-attempt HTTP timeout in seconds for Ollama calls |
| `CORS_ORIGINS` | Backend | No | `""` | Comma-separated list of additional allowed origins (wildcard `*` is ignored) |
| `VITE_API_BASE_URL` | Frontend | No | `"http://localhost:8000"` | Backend API base URL compiled into the Vite frontend bundle |

---

## 14. Docker Setup

[`docker-compose.yml`](docker-compose.yml) orchestrates PostgreSQL 16, the FastAPI backend, and the React frontend with healthcheck-ordered startup:

```bash
# Build and start all three containers in the foreground
docker compose up --build

# Or run in detached mode
docker compose up --build -d

# Stop and remove containers
docker compose down
```

### Container Services & Ports
| Service | Container Name | Image / Dockerfile | Host -> Container Port | Startup & Health Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `db` | `ai-code-review-db` | `postgres:16-alpine` | `55432:5432` | Persists data in `postgres_data` volume; healthchecked via `pg_isready` |
| `api` | `ai-code-review-api` | [`./Dockerfile`](Dockerfile) (`python:3.12-slim` + `git`) | `8000:8000` | Waits for `db` healthy; runs `/app/scripts/start.sh` (`alembic upgrade head` -> `uvicorn`); healthchecked via `GET /api/v1/ready` |
| `frontend` | `ai-code-review-frontend` | [`./frontend/Dockerfile`](frontend/Dockerfile) (`node:20-alpine`) | `5173:5173` | Waits for `api` healthy; runs `npm run dev -- --host 0.0.0.0` |

> **Note:** In [`docker-compose.yml`](docker-compose.yml), the `api` container uses self-contained defaults (`DOCKER_SECRET_KEY`, `DOCKER_APP_ENV`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) so a local `.env` pointing to a cloud database does not accidentally override the container's internal `@db:5432` connection.

---

## 15. Testing and Quality Checks

### Backend Test Suite (`43` Unit & Regression Tests)
Located in [`tests/`](tests/) and runnable via Python's built-in `unittest` discovery:
- [`tests/test_scanner_accuracy.py`](tests/test_scanner_accuracy.py) — Verifies all 14 static security rules across Python, JS/TS, Java, and C/C++, and confirms comments/docstrings do not trigger false positives while line numbers remain exact.
- [`tests/test_github_service.py`](tests/test_github_service.py) — Verifies HTTPS GitHub URL allowlisting, rejection of flag injection (`-u`, `--upload-pack`), rejection of non-GitHub/SSRF URLs, hardened Git environment variables (`GIT_TERMINAL_PROMPT=0`, `protocol.https.allow=always`), and temporary directory cleanup on clone failure/timeout.
- [`tests/test_repository_scanner.py`](tests/test_repository_scanner.py) — Verifies `MAX_FILES`, `MAX_FILE_SIZE_BYTES`, scan deadline enforcement, and ignored directory filtering.
- [`tests/test_repository_review_route.py`](tests/test_repository_review_route.py) — Verifies JWT authentication on `/repository-review` and `/repository-review/export-pdf`, per-user rate limiting (`429 Too Many Requests` + `Retry-After`), `MAX_SUBMISSION_CODE_LENGTH` (`100,000`), and log redaction in `OllamaReviewProvider`.
- [`tests/test_email_normalization.py`](tests/test_email_normalization.py) — Verifies case-insensitive signup/login, schema normalization, and Alembic migration `0002_case_insensitive_email` upgrade/downgrade and fail-fast duplicate detection without leaking PII.
- [`tests/test_pagination.py`](tests/test_pagination.py) — Verifies `limit`/`offset` bounds, deterministic ordering, and strict user ownership isolation on `/submissions` and `/reviews`.
- [`tests/test_cors_config.py`](tests/test_cors_config.py) — Verifies CORS origin parsing and rejection of wildcard `*` origins.

```bash
# Run backend import smoke test (same command as GitHub Actions CI)
DATABASE_URL=sqlite:///./test.db SECRET_KEY=github-actions-secret-key-123456789012345 \
  python -c "from app.main import app; print('Backend OK')"

# Run all 43 backend tests
python -m unittest discover tests
```

### Frontend Tests, Linting & Production Build (`6` Tests)
Located in [`frontend/tests/guest_demo.test.mjs`](frontend/tests/guest_demo.test.mjs):
- Verifies landing-page Guest Demo CTA link (`/demo`), unauthenticated rendering of `GuestDemoPage`, presence of sample scores/findings/remediation guidance, conversion links to `/signup` and `/login`, strict isolation from protected API modules, and [`frontend/vercel.json`](frontend/vercel.json) SPA fallback rewrite rules.

```bash
# Run the 6 frontend Node tests
npm --prefix frontend test

# Run ESLint
npm --prefix frontend run lint

# Run TypeScript compiler check and Vite production build
npm --prefix frontend run build

# Validate Docker Compose syntax
docker compose config -q
```

### Continuous Integration (`.github/workflows/ci.yml`)
On every `push` and `pull_request` to `main`/`master`, [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs:
1. **`frontend` job:** `npm ci` -> `npm run build` -> `npm test` on Node.js `20`.
2. **`backend` job:** `pip install -r requirements.txt` -> FastAPI import check -> `python -m unittest discover tests` on Python `3.12`.
3. **`docker` job:** `docker build -t ai-code-reviewer-api .` (runs after both `frontend` and `backend` pass).

---

## 16. Deployment

### Frontend (Vercel)
- **Root Directory:** `frontend`
- **Build Command:** `npm run build` (`tsc -b && vite build`)
- **Output Directory:** `dist`
- **SPA Routing:** [`frontend/vercel.json`](frontend/vercel.json) rewrites `/(.*)` to `/index.html` so direct navigation and page refreshes on `/demo`, `/login`, `/signup`, `/dashboard`, and `/reviews/:id` resolve cleanly without `404` errors.
- **Required Environment Variable:** `VITE_API_BASE_URL=https://ai-code-reviewer-api-wgz8.onrender.com`

### Backend (Render)
- **Runtime:** Docker using root [`Dockerfile`](Dockerfile) (`python:3.12-slim` with `git` installed and non-root `app` user).
- **Startup & Migration Execution:** Container `CMD` executes [`/app/scripts/start.sh`](scripts/start.sh), which runs `python -m alembic upgrade head` under `set -eu` before `exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`. If a migration fails, startup aborts immediately before the API serves traffic.
- **Required Environment Variables on Render:**
  - `DATABASE_URL` (PostgreSQL connection URL)
  - `SECRET_KEY` (random secret `>= 32` characters)
  - `APP_ENV=production`
  - `DEBUG=false`
  - `AI_PROVIDER=mock`
  - `CORS_ORIGINS=https://ai-code-reviewer-seven-brown.vercel.app`

---

## 17. Security Measures

- **Password & Token Security:** Passwords (`8–72` chars) are hashed with `passlib[bcrypt]`; JWT bearer tokens are signed with `HS256` and require a `SECRET_KEY` of at least `32` characters (enforced by Pydantic validators, with placeholder keys rejected in `production`).
- **Case-Insensitive Email Uniqueness:** Enforced at both the application layer (`value.strip().lower()` and `func.lower(User.email)`) and the PostgreSQL schema layer via the unique index `ix_users_lower_email` on `lower(email)`.
- **SSRF & Git Argument Injection Prevention ([`app/services/github_service.py`](app/services/github_service.py)):**
  - Rejects any URL starting with `-` and passes `--` before positional operands in `git clone --depth 1 -- <url> <temp_dir>`.
  - Allows only canonical `https://github.com/<owner>/<repo>` URLs and blocks `.` / `..` path traversal segments.
  - Runs `git` with `GIT_TERMINAL_PROMPT=0` and `protocol.allow=never` + `protocol.https.allow=always` so HTTP redirects cannot pivot to `file://`, `ssh://`, `git://`, or plain `http://`.
- **DoS & Resource Exhaustion Controls:**
  - `SubmissionCreate.code` is bounded to `100,000` characters (`MAX_SUBMISSION_CODE_LENGTH`).
  - Repository scans are bounded to `500` files, `500 KB` per file, a `60s` clone timeout, and a `30s` scan deadline, with guaranteed temporary directory cleanup in `finally`.
  - Authenticated sliding-window rate limits enforce `5 req / 60s` on repository review routes and `10 req / 60s` on review generation routes.
- **Log & Secret Hygiene:** `OllamaReviewProvider` and `AIReviewService` log only character lengths at `DEBUG` level and never print raw LLM outputs or submitted source code to `stdout`.

---

## 18. Current Limitations

1. **Regex-Based Static Scanner:** [`static_scanner.py`](app/services/security/static_scanner.py) masks comments/docstrings and matches 14 regular expressions line-by-line. It does not build an AST, track variable taint across functions/files, or scan third-party lockfiles for CVEs.
2. **Supported Repository File Extensions:** Repository scans only inspect `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, and `.h` files (`<= 500 KB` each, up to `500` files per repo). Other languages (e.g., Go, Rust, Ruby, PHP) are currently skipped during repository walks.
3. **Cloud Deployment Uses `AI_PROVIDER=mock`:** Because the Render web service does not have a co-located Ollama GPU instance, the live hosted backend runs with `AI_PROVIDER=mock` (combining real static security findings and score penalties with the deterministic mock AI baseline). Real LLM inference via `AI_PROVIDER=ollama` requires running the backend against a local or self-hosted Ollama server.
4. **Public GitHub Repositories Only:** `/repository-review` clones unauthenticated public repositories on `github.com`. Private repositories or repositories hosted on GitLab/Bitbucket are rejected.
5. **In-Memory Rate Limiting:** [`RateLimiter`](app/core/rate_limit.py) stores request timestamps in process memory per worker; it is not backed by Redis across multiple instances.
6. **Ephemeral Repository Scans:** Unlike single-file code reviews (which are saved in PostgreSQL under `submissions` and `reviews`), repository scan results are computed on demand and returned directly (or exported as a PDF) without being stored in a database table.
7. **Render Free-Tier Cold Starts:** After periods of inactivity, the hosted Render backend container may take `30–50 seconds` to wake up on the first request.

---

## 19. Roadmap / Future Improvements

The following enhancements are genuine candidates for future iterations (none of these are currently implemented):
- **Persistence for Repository Scans:** Add database tables to store historical repository scan reports and track repository health score trends over time.
- **Hosted Cloud LLM Providers:** Add optional provider adapters for hosted APIs (e.g., Google Gemini, OpenAI, or Anthropic) alongside the existing `mock` and local `ollama` providers.
- **AST-Based Analysis & Dependency Auditing:** Augment the regex scanner with Python `ast` / Tree-sitter rules and lockfile vulnerability checks (`requirements.txt`, `package-lock.json`).
- **GitHub OAuth & Private Repository Access:** Support GitHub OAuth sign-in and fine-grained personal access tokens for scanning private repositories and pull request diffs.
- **Distributed Rate Limiting & Background Workers:** Move repository cloning and LLM review jobs to a task queue (e.g., Celery/RQ + Redis) with shared Redis rate limiting.

---

## 20. Contributing

Contributions, bug reports, and security improvements are welcome:

1. **Fork** the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Make your changes** and add unit tests in [`tests/`](tests/) (backend) or [`frontend/tests/`](frontend/tests/) (frontend).
3. **Run the verification suite locally** before opening a pull request:
   ```bash
   python -m unittest discover tests
   npm --prefix frontend test
   npm --prefix frontend run lint
   npm --prefix frontend run build
   git diff --check
   ```
4. **Open a Pull Request** against `main` with a clear description of the problem and solution.

---

## 21. License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for full text (`Copyright (c) 2026 Nikhil VS`).

---

## Author

**Nikhil VS**
- **GitHub:** [https://github.com/Nikhil-VS1811](https://github.com/Nikhil-VS1811)
- **LinkedIn:** [https://www.linkedin.com/in/nikhil-vs/](https://www.linkedin.com/in/nikhil-vs/)
