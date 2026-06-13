import logging
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.api.routes import auth, health, reviews, submissions
from app.api.routes import repository_review
from app.core.config import settings


logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s completed with %s in %sms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="0.1.0",
    )
    

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-code-reviewer-seven-brown.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
    app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(
    repository_review.router,
    prefix="/repository-review",
    tags=["Repository Review"],
)

    return app


app = create_app()
