from pydantic import BaseModel


class RepositoryFinding(BaseModel):
    file: str
    line_number: int
    severity: str
    category: str
    comment: str


class RepositoryPdfRequest(BaseModel):
    files_scanned: int
    issues_found: int

    critical: int
    high: int
    medium: int
    low: int

    repository_health_score: int

    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

    findings: list[RepositoryFinding]