from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.auth_service import get_current_user
from app.services.submission_service import (
    create_submission,
    delete_user_submission,
    get_user_submission,
    list_user_submissions,
)


router = APIRouter()


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_code(
    payload: SubmissionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return create_submission(db=db, payload=payload, current_user=current_user)


@router.get("", response_model=list[SubmissionResponse])
def read_submissions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SubmissionResponse]:
    return list_user_submissions(db=db, current_user=current_user)


@router.get("/{submission_id}", response_model=SubmissionResponse)
def read_submission(
    submission_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return get_user_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    submission_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    delete_user_submission(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
