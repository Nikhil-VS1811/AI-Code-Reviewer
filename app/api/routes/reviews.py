from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.rate_limit import review_generation_rate_limiter
from app.db.database import get_db
from app.models.user import User
from app.schemas.review import ReviewResponse
from app.services.auth_service import get_current_user
from app.services.pdf_report_service import generate_review_pdf
from app.services.review_generation_service import generate_review_for_submission
from app.services.review_service import get_user_review, list_user_reviews


router = APIRouter()


@router.post("/generate/{submission_id}", response_model=ReviewResponse)
def generate_review(
    submission_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    _rate_limit: Annotated[None, Depends(review_generation_rate_limiter)],
) -> ReviewResponse:
    return generate_review_for_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )


@router.get("", response_model=list[ReviewResponse])
def read_reviews(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ReviewResponse]:
    return list_user_reviews(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def read_review(
    review_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ReviewResponse:
    return get_user_review(db=db, review_id=review_id, current_user=current_user)


@router.get("/{review_id}/pdf")
def export_review_pdf(
    review_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    review = get_user_review(db=db, review_id=review_id, current_user=current_user)
    pdf = generate_review_pdf(review)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="review-{review.id}.pdf"',
        },
    )
