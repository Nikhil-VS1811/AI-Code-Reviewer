import asyncio
import json
import unittest

from app.main import app


class TestRepositoryReviewAuth(unittest.TestCase):
    def _run_asgi(self, method: str, path: str, headers: list = None, body: bytes = b""):
        headers = headers or []
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [(k.lower().encode(), v.encode()) for k, v in headers],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        messages = []

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            messages.append(message)

        asyncio.run(app(scope, receive, send))
        status_code = next(m["status"] for m in messages if m["type"] == "http.response.start")
        body_parts = [m.get("body", b"") for m in messages if m["type"] == "http.response.body"]
        return status_code, b"".join(body_parts)

    def test_unauthenticated_review_repository_is_rejected(self):
        body = json.dumps({"repo_url": "https://github.com/pallets/flask"}).encode("utf-8")
        headers = [("Content-Type", "application/json")]

        status_code, response_body = self._run_asgi("POST", "/repository-review/", headers, body)
        self.assertEqual(status_code, 401)
        self.assertIn(b"Not authenticated", response_body)

    def test_unauthenticated_export_pdf_is_rejected(self):
        body = json.dumps({"repo_url": "https://github.com/pallets/flask"}).encode("utf-8")
        headers = [("Content-Type", "application/json")]

        status_code, response_body = self._run_asgi("POST", "/repository-review/export-pdf", headers, body)
        self.assertEqual(status_code, 401)
        self.assertIn(b"Not authenticated", response_body)

    def test_unauthenticated_submissions_endpoint_is_rejected(self):
        status_code, response_body = self._run_asgi("GET", "/submissions")
        self.assertEqual(status_code, 401)
        self.assertIn(b"Not authenticated", response_body)

    def test_unauthenticated_reviews_endpoint_is_rejected(self):
        status_code, response_body = self._run_asgi("GET", "/reviews")
        self.assertEqual(status_code, 401)
        self.assertIn(b"Not authenticated", response_body)

    def test_submission_code_length_limit_enforced(self):
        from pydantic import ValidationError
        from app.schemas.submission import MAX_SUBMISSION_CODE_LENGTH, SubmissionCreate

        valid = SubmissionCreate(
            language="python",
            code="x" * MAX_SUBMISSION_CODE_LENGTH,
        )
        self.assertEqual(len(valid.code), MAX_SUBMISSION_CODE_LENGTH)

        with self.assertRaises(ValidationError):
            SubmissionCreate(
                language="python",
                code="x" * (MAX_SUBMISSION_CODE_LENGTH + 1),
            )

    def test_repository_scan_rate_limiter_returns_429_when_exceeded(self):
        from unittest.mock import patch
        from app.core.rate_limit import repository_scan_rate_limiter
        from app.models.user import User
        from app.services.auth_service import get_current_user

        test_user = User(
            id=99,
            username="ratelimituser",
            email="ratelimit@example.com",
            hashed_password="pw",
        )
        repository_scan_rate_limiter.reset()
        app.dependency_overrides[get_current_user] = lambda: test_user

        body = json.dumps({"repo_url": "https://github.com/pallets/flask"}).encode("utf-8")
        headers = [("Content-Type", "application/json")]

        fake_report = {
            "files_scanned": 1,
            "issues_found": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "findings": [],
            "repository_health_score": 100,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
        }

        try:
            with patch(
                "app.api.routes.repository_review.analyze_repository",
                return_value=fake_report,
            ):
                for _ in range(repository_scan_rate_limiter.max_requests):
                    status_code, _ = self._run_asgi(
                        "POST", "/repository-review/", headers, body
                    )
                    self.assertEqual(status_code, 200)

                status_code, response_body = self._run_asgi(
                    "POST", "/repository-review/", headers, body
                )
                self.assertEqual(status_code, 429)
                self.assertIn(b"Rate limit exceeded", response_body)
        finally:
            app.dependency_overrides.pop(get_current_user, None)
            repository_scan_rate_limiter.reset()

    def test_ollama_provider_does_not_print_or_log_raw_sensitive_code(self):
        import io
        from contextlib import redirect_stdout
        from unittest.mock import MagicMock, patch
        from app.services.providers.ollama_provider import OllamaReviewProvider

        provider = OllamaReviewProvider(model="qwen3:4b", base_url="http://localhost:11434")
        sensitive_marker = "SUPER_SECRET_PROPRIETARY_SNIPPET_987654"
        fake_review_json = json.dumps(
            {
                "overall_score": 80,
                "security_score": 80,
                "performance_score": 80,
                "maintainability_score": 80,
                "readability_score": 80,
                "summary": f"Summary referencing {sensitive_marker}",
                "comments": [],
            }
        )
        fake_http_body = json.dumps({"response": fake_review_json}).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_http_body
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False

        stdout_buf = io.StringIO()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertLogs("app.services.providers.ollama_provider", level="DEBUG") as cm:
                with redirect_stdout(stdout_buf):
                    result = provider.generate_structured_review(prompt=sensitive_marker)

        self.assertEqual(result.overall_score, 80)
        self.assertEqual(stdout_buf.getvalue(), "")
        combined_logs = "\n".join(cm.output)
        self.assertNotIn(sensitive_marker, combined_logs)


if __name__ == "__main__":
    unittest.main()
