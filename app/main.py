from fastapi import FastAPI

from app.api.routes import auth, health, reviews, submissions
from app.core.config import settings
from app.db.database import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="0.1.0",
    )

    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
    app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
