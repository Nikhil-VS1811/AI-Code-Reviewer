from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.health import HealthResponse, ReadinessResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", message="AI Code Review System API is running")


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(db: Annotated[Session, Depends(get_db)]) -> ReadinessResponse:
    checks = {"database": "ok"}

    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        checks["database"] = "unavailable"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "checks": checks},
        ) from exc

    return ReadinessResponse(status="ok", checks=checks)
