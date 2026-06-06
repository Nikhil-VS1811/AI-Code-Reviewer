import json
import logging
import time
from typing import Literal
from urllib import error, request

from pydantic import ValidationError

from app.services.ai_review_service import (
    AIReviewProvider,
    AIReviewResult,
    normalize_review_scores,
)


logger = logging.getLogger(__name__)


SupportedOllamaModel = Literal["qwen3:4b", "llama3.1:8b", "qwen2.5-coder:7b"]
SUPPORTED_OLLAMA_MODELS = {"qwen3:4b", "llama3.1:8b", "qwen2.5-coder:7b"}


class OllamaReviewProvider(AIReviewProvider):
    def __init__(
        self,
        model: SupportedOllamaModel = "qwen3:4b",
        base_url: str = "http://localhost:11434",
        timeout_seconds: int = 60,
        max_retries: int = 2,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        if model not in SUPPORTED_OLLAMA_MODELS:
            raise ValueError(f"Unsupported Ollama model: {model}")

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def generate_review(self, prompt: str) -> str:
        review = self.generate_structured_review(prompt=prompt)
        return review.model_dump_json()

    def generate_structured_review(self, prompt: str) -> AIReviewResult:
        raw_response = self._call_ollama(prompt=prompt)
        response_text = self._extract_ollama_response(raw_response=raw_response)
        return self._parse_review_response(response_text=response_text)

    def _call_ollama(self, prompt: str) -> dict:
        payload = {
            "model": self.model,
            "prompt": self._build_ollama_prompt(prompt=prompt),
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }
        logger.debug("Sending review prompt to Ollama model %s.", self.model)
        encoded_payload = json.dumps(payload).encode("utf-8")
        ollama_request = request.Request(
            url=f"{self.base_url}/api/generate",
            data=encoded_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with request.urlopen(
                    ollama_request,
                    timeout=self.timeout_seconds,
                ) as response:
                    response_body = response.read().decode("utf-8")
                    logger.debug("Ollama raw HTTP response: %s", response_body)
                    return json.loads(response_body)
            except TimeoutError as exc:
                logger.warning("Ollama request timed out on attempt %s.", attempt + 1)
                last_error = exc
            except error.URLError as exc:
                logger.warning("Ollama request failed on attempt %s: %s", attempt + 1, exc)
                last_error = exc
            except json.JSONDecodeError as exc:
                logger.exception("Ollama returned malformed HTTP response JSON.")
                raise ValueError("Ollama returned invalid response JSON.") from exc

            if attempt < self.max_retries:
                time.sleep(self.retry_delay_seconds)

        raise TimeoutError("Ollama request failed after retries.") from last_error

    def _build_ollama_prompt(self, prompt: str) -> str:
        return f"""
{prompt}

Important Ollama JSON requirements:
- Return exactly one JSON object.
- All score fields must be integers from 0 to 100.
- Do not return -1 or any negative number.
- If a score is uncertain, choose a reasonable value between 0 and 100.
- Include all required fields: overall_score, security_score, performance_score,
  maintainability_score, readability_score, summary, comments.
""".strip()

    def _extract_ollama_response(self, raw_response: dict) -> str:
        response_text = raw_response.get("response")
        if not isinstance(response_text, str) or not response_text.strip():
            raise ValueError("Ollama response did not include review JSON.")

        logger.debug("Ollama generated review JSON text: %s", response_text)
        return response_text.strip()

    def _parse_review_response(self, response_text: str) -> AIReviewResult:
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as exc:
            logger.exception("Ollama review output was malformed JSON.")
            raise ValueError(f"Ollama review output was malformed JSON: {exc}") from exc

        try:
            response_data = normalize_review_scores(response_data)
            return AIReviewResult.model_validate(response_data)
        except ValidationError as exc:
            logger.warning("Ollama review validation failed: %s", exc.errors())
            raise ValueError(
                f"Ollama review output did not match the expected schema: {exc}"
            ) from exc
