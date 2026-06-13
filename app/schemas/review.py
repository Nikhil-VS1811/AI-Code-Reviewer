from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCommentResponse(BaseModel):
    id: int
    review_id: int
    line_number: int
    severity: str
    category: str
    comment: str

    model_config = ConfigDict(from_attributes=True)


class ReviewResponse(BaseModel):
    id: int
    submission_id: int
    overall_score: int
    security_score: int
    performance_score: int
    maintainability_score: int
    readability_score: int
    summary: str
    created_at: datetime
    comments: list[ReviewCommentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
