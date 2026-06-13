import json
import logging
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.models.submission import Submission


logger = logging.getLogger(__name__)


class AIReviewComment(BaseModel):
    line_number: int = Field(ge=1)
    severity: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=100)
    comment: str = Field(min_length=1)


class AIReviewResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    security_score: int = Field(ge=0, le=100)
    performance_score: int = Field(ge=0, le=100)
    maintainability_score: int = Field(ge=0, le=100)
    readability_score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    comments: list[AIReviewComment] = Field(default_factory=list)


class AIReviewProvider(Protocol):
    def generate_review(self, prompt: str) -> str:
        pass


class MockAIReviewProvider:
    def generate_review(self, prompt: str) -> str:
        return json.dumps(
            {
                "overall_score": 82,
                "security_score": 78,
                "performance_score": 84,
                "maintainability_score": 80,
                "readability_score": 86,
                "summary": (
                    "Mock AI review: the code is generally readable, but it would "
                    "benefit from stronger input validation, clearer function "
                    "boundaries, and small performance-minded cleanups."
                ),
                "comments": [
                    {
                        "line_number": 1,
                        "severity": "medium",
                        "category": "security",
                        "comment": "Validate external input before using it in business logic.",
                    },
                    {
                        "line_number": 3,
                        "severity": "low",
                        "category": "readability",
                        "comment": "Consider using clearer variable names to make the intent easier to follow.",
                    },
                    {
                        "line_number": 6,
                        "severity": "medium",
                        "category": "maintainability",
                        "comment": "Split complex logic into smaller functions so each unit has one responsibility.",
                    },
                    {
                        "line_number": 10,
                        "severity": "low",
                        "category": "performance",
                        "comment": "Avoid repeated work inside loops when values can be calculated once beforehand.",
                    },
                ],
            }
        )


class AIReviewService:
    def __init__(self, provider: AIReviewProvider | None = None) -> None:
        self.provider = provider or MockAIReviewProvider()

    def review_code(self, submission: Submission) -> AIReviewResult:
        prompt = self.build_prompt(submission=submission)
        raw_response = self.provider.generate_review(prompt=prompt)
        return self.parse_response(raw_response=raw_response)

    def build_prompt(self, submission: Submission) -> str:
        return f"""
You are an expert AI code reviewer.

Review the following {submission.language} code and return only valid JSON.
Do not include Markdown, explanations, comments, or text outside the JSON object.

Scoring rules:
- Every score must be an integer from 0 to 100.
- Never return negative scores.
- Never return -1 for unknown or unavailable scores.
- If you are uncertain, choose the best reasonable score between 0 and 100.

Required JSON shape:
{{
  "overall_score": 75,
  "security_score": 75,
  "performance_score": 75,
  "maintainability_score": 75,
  "readability_score": 75,
  "summary": "",
  "comments": [
    {{
      "line_number": 1,
      "severity": "low|medium|high",
      "category": "security|performance|maintainability|readability",
      "comment": ""
    }}
  ]
}}

Code:
```{submission.language}
{submission.code}
```
""".strip()

    def parse_response(self, raw_response: str) -> AIReviewResult:
        logger.debug("AI provider raw response: %s", raw_response)
        try:
            response_data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            logger.exception("AI provider returned malformed JSON.")
            raise ValueError(f"AI provider returned malformed JSON: {exc}") from exc

        response_data = normalize_review_scores(response_data)

        try:
            return AIReviewResult.model_validate(response_data)
        except ValidationError as exc:
            logger.warning("AI review validation failed: %s", exc.errors())
            raise ValueError(f"AI provider returned an invalid review structure: {exc}") from exc


def normalize_review_scores(response_data: object) -> object:
    if not isinstance(response_data, dict):
        return response_data

    normalized_data = response_data.copy()
    for field_name in (
        "overall_score",
        "security_score",
        "performance_score",
        "maintainability_score",
        "readability_score",
    ):
        if field_name not in normalized_data:
            continue

        normalized_data[field_name] = normalize_score(normalized_data[field_name])

    return normalized_data


def normalize_score(value: object) -> object:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return min(100, max(0, value))

    if isinstance(value, float):
        return min(100, max(0, round(value)))

    if isinstance(value, str):
        try:
            return min(100, max(0, round(float(value))))
        except ValueError:
            return value

    return value


def get_ai_review_provider() -> AIReviewProvider:
    provider_name = settings.AI_PROVIDER.lower()
    if provider_name == "ollama":
        from app.services.providers.ollama_provider import OllamaReviewProvider

        return OllamaReviewProvider(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
        )

    if provider_name == "mock":
        return MockAIReviewProvider()

    raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")


def get_ai_review_service() -> AIReviewService:
    return AIReviewService(provider=get_ai_review_provider())
