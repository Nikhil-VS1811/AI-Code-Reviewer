from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


MAX_SUBMISSION_CODE_LENGTH = 100_000


class SubmissionCreate(BaseModel):
    language: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=MAX_SUBMISSION_CODE_LENGTH)


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    language: str
    code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
