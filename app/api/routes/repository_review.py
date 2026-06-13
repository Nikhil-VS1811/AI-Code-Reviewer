from fastapi import APIRouter

from app.schemas.repository_review import (
    RepositoryReviewRequest,
)
from app.services.repository_review_service import (
    analyze_repository,
)
from fastapi import Response

from app.services.repository_pdf_service import (
    RepositoryReport,
    RepositoryFinding,
    generate_repository_pdf,
)


router = APIRouter()


@router.post("/")
def review_repository(
    payload: RepositoryReviewRequest,
):
    return analyze_repository(
        payload.repo_url
    )


@router.post("/export-pdf")
def export_repository_pdf(
    payload: RepositoryReviewRequest,
):
    report_data = analyze_repository(
        payload.repo_url
    )

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
            "Content-Disposition":
            'attachment; filename="repository-report.pdf"'
        },
    )