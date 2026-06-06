from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.review import Review
from app.models.submission import Submission
from app.models.user import User


def list_user_reviews(db: Session, current_user: User) -> list[Review]:
    statement = (
        select(Review)
        .join(Submission)
        .options(selectinload(Review.comments))
        .where(Submission.user_id == current_user.id)
        .order_by(Review.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_user_review(db: Session, review_id: int, current_user: User) -> Review:
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
