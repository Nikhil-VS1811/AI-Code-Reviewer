from pydantic import BaseModel, Field


class RepositoryReviewRequest(BaseModel):
    repo_url: str = Field(min_length=1, max_length=512)