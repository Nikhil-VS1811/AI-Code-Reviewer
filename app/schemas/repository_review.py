from pydantic import BaseModel


class RepositoryReviewRequest(BaseModel):
    repo_url: str