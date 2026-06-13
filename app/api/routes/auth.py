from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)


router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    return create_user(db=db, payload=payload)


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.post("/login/json", response_model=Token)
def login_json(
    payload: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = authenticate_user(db=db, email=payload.email, password=payload.password)
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return current_user
