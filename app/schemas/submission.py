from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    language: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1)


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    language: str
    code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
