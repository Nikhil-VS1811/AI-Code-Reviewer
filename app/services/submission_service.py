from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import SubmissionCreate


def create_submission(
    db: Session,
    payload: SubmissionCreate,
    current_user: User,
) -> Submission:
    submission = Submission(
        user_id=current_user.id,
        language=payload.language,
        code=payload.code,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_user_submissions(db: Session, current_user: User) -> list[Submission]:
    statement = (
        select(Submission)
        .where(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_user_submission(
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


def delete_user_submission(
    db: Session,
    submission_id: int,
    current_user: User,
) -> None:
    submission = get_user_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )
    db.delete(submission)
    db.commit()
