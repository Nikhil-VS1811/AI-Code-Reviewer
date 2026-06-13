from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    message: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]
