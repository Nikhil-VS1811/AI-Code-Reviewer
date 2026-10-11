import unittest
from unittest.mock import patch

from app.main import get_allowed_cors_origins


class TestCorsConfiguration(unittest.TestCase):
    def test_default_origins_present(self):
        origins = get_allowed_cors_origins()
        self.assertIn("http://localhost:5173", origins)
        self.assertIn("https://ai-code-reviewer-seven-brown.vercel.app", origins)

    @patch("app.main.settings")
    def test_configured_origins_merged_and_deduplicated(self, mock_settings):
        mock_settings.cors_origins = [
            "http://localhost:3000",
            "http://localhost:5173",  # duplicate of base
            "https://custom-preview.domain.com",
            "",
        ]
        origins = get_allowed_cors_origins()
        self.assertIn("http://localhost:3000", origins)
        self.assertIn("https://custom-preview.domain.com", origins)
        self.assertIn("http://localhost:5173", origins)
        # Verify deduplication
        self.assertEqual(origins.count("http://localhost:5173"), 1)

    @patch("app.main.settings")
    def test_wildcard_rejected_when_credentials_used(self, mock_settings):
        mock_settings.cors_origins = ["*", "http://valid.domain.com"]
        origins = get_allowed_cors_origins()
        self.assertNotIn("*", origins)
        self.assertIn("http://valid.domain.com", origins)


if __name__ == "__main__":
    unittest.main()
