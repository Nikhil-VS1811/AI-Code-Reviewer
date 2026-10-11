import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.rate_limit import repository_scan_rate_limiter
from app.models.user import User
from app.schemas.repository_review import (
    RepositoryReviewRequest,
)
from app.services.auth_service import get_current_user
from app.services.repository_review_service import (
    analyze_repository,
)
from app.services.repository_pdf_service import (
    RepositoryReport,
    RepositoryFinding,
    generate_repository_pdf,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
@router.post("/", status_code=status.HTTP_200_OK)
def review_repository(
    payload: RepositoryReviewRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _rate_limit: Annotated[None, Depends(repository_scan_rate_limiter)],
):
    try:
        return analyze_repository(payload.repo_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Repository review failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze repository.",
        ) from exc


@router.post("/export-pdf")
def export_repository_pdf(
    payload: RepositoryReviewRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _rate_limit: Annotated[None, Depends(repository_scan_rate_limiter)],
):
    try:
        report_data = analyze_repository(payload.repo_url)

        report = RepositoryReport(
            files_scanned=report_data["files_scanned"],
            issues_found=report_data["issues_found"],
            critical=report_data["critical"],
            high=report_data["high"],
            medium=report_data["medium"],
            low=report_data["low"],
            repository_health_score=report_data["repository_health_score"],
            strengths=report_data["strengths"],
            weaknesses=report_data["weaknesses"],
            recommendations=report_data["recommendations"],
            findings=[
                RepositoryFinding(**finding)
                for finding in report_data["findings"]
            ],
        )

        pdf = generate_repository_pdf(report)

        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="repository-report.pdf"'
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Repository PDF export failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export repository report PDF.",
        ) from exc