import logging
from app.services.security.static_scanner import scan_code
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.services.ai_review_service import (
    AIReviewService,
    AIReviewComment,
    get_ai_review_service,
)

from app.models.review import Review, ReviewComment
from app.models.submission import Submission
from app.models.user import User


logger = logging.getLogger(__name__)


def generate_review_for_submission(
    db: Session,
    submission_id: int,
    current_user: User,
    ai_review_service: AIReviewService | None = None,
) -> Review:
    submission = _get_owned_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )
    _ensure_review_does_not_exist(db=db, submission_id=submission.id)

    try:
        review_service = ai_review_service or get_ai_review_service()
        static_findings = scan_code(submission.code)
        ai_review = review_service.review_code(submission=submission)
        for finding in static_findings:
            ai_review.comments.append(AIReviewComment(line_number=finding["line_number"],severity=finding["severity"],category=finding["category"],comment=finding["comment"],))

        critical_count = sum(
        1
        for finding in static_findings
        if finding["severity"] == "critical"
        )

        high_count = sum(
        1
        for finding in static_findings
        if finding["severity"] == "high"
        )

        penalty = critical_count * 20 + high_count * 10

        ai_review.security_score = max(
        0,
        ai_review.security_score - penalty,
        )

        ai_review.overall_score = max(
        0,
        ai_review.overall_score - penalty // 2,
        )

    except ValueError as exc:
        logger.warning("AI review provider returned an invalid response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI review provider returned an invalid response: {exc}",
        ) from exc
    except TimeoutError as exc:
        logger.warning("AI review provider timed out: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI review provider timed out.",
        ) from exc

    try:
        review = Review(
            submission_id=submission.id,
            overall_score=ai_review.overall_score,
            security_score=ai_review.security_score,
            performance_score=ai_review.performance_score,
            maintainability_score=ai_review.maintainability_score,
            readability_score=ai_review.readability_score,
            summary=ai_review.summary,
        )
        db.add(review)
        db.flush()

        comments = [
            ReviewComment(review_id=review.id, **comment.model_dump())
            for comment in ai_review.comments
        ]
        db.add_all(comments)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate review.",
        ) from exc

    return _get_review_with_comments(db=db, review_id=review.id, current_user=current_user)


def _get_owned_submission(
    db: Session,
    submission_id: int,
    current_user: User,
) -> Submission:
    statement = select(Submission).where(
        Submission.id == submission_id,
        Submission.user_id == current_user.id,
    )
    submission = db.scalar(statement)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )

    return submission


def _ensure_review_does_not_exist(db: Session, submission_id: int) -> None:
    statement = select(Review.id).where(Review.submission_id == submission_id)
    existing_review_id = db.scalar(statement)
    if existing_review_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A review already exists for this submission.",
        )


def _get_review_with_comments(
    db: Session,
    review_id: int,
    current_user: User,
) -> Review:
    statement = (
        select(Review)
        .join(Submission)
        .options(selectinload(Review.comments))
        .where(
            Review.id == review_id,
            Submission.user_id == current_user.id,
        )
    )
    review = db.scalar(statement)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    return review
