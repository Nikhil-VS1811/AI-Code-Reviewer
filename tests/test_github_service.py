import subprocess
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.services.github_service import (
    validate_github_url,
    clone_repository,
    cleanup_repository,
)


class TestGithubServiceUrlValidation(unittest.TestCase):
    def test_valid_github_urls(self):
        valid_urls = [
            "https://github.com/pallets/flask",
            "https://github.com/pallets/flask.git",
            "https://github.com/pallets/flask/",
            "https://github.com/pallets/flask.git/",
            "https://github.com/fastapi/fastapi",
            "https://github.com/Nikhil-VS1811/AI-Code-Reviewer",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                normalized = validate_github_url(url)
                self.assertTrue(normalized.startswith("https://github.com/"))
                self.assertTrue(normalized.endswith(".git"))

    def test_reject_non_https(self):
        invalid_urls = [
            "http://github.com/pallets/flask",
            "git://github.com/pallets/flask.git",
            "ssh://git@github.com/pallets/flask.git",
            "ftp://github.com/pallets/flask",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_github_url(url)

    def test_reject_flag_and_option_injection(self):
        injections = [
            "--upload-pack=id",
            "-o/tmp/evil",
            "--config=core.gitProxy=evil",
            "-v",
        ]
        for injection in injections:
            with self.subTest(injection=injection):
                with self.assertRaises(ValueError):
                    validate_github_url(injection)

    def test_reject_other_domains(self):
        other_domains = [
            "https://gitlab.com/owner/repo",
            "https://bitbucket.org/owner/repo",
            "https://evil.com/github.com/owner/repo",
            "https://169.254.169.254/owner/repo",
            "https://localhost/owner/repo",
        ]
        for url in other_domains:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_github_url(url)

    def test_reject_path_traversal_and_invalid_formats(self):
        invalid_paths = [
            "https://github.com/../evil",
            "https://github.com/./evil",
            "https://github.com/owner",
            "https://github.com/",
            "",
            "   ",
        ]
        for path in invalid_paths:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    validate_github_url(path)

    def test_reject_non_string(self):
        with self.assertRaises(ValueError):
            validate_github_url(None)
        with self.assertRaises(ValueError):
            validate_github_url(12345)


class TestGithubServiceClone(unittest.TestCase):
    @patch("app.services.github_service.subprocess.run")
    def test_clone_invokes_safe_arguments(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        repo_url = "https://github.com/pallets/flask"

        path = clone_repository(repo_url, timeout_seconds=10)
        self.assertTrue(path.exists())

        # Verify safe argument structure with '--' separator
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "git")
        self.assertEqual(cmd[1], "clone")
        self.assertEqual(cmd[2], "--depth")
        self.assertEqual(cmd[3], "1")
        self.assertEqual(cmd[4], "--")
        self.assertEqual(cmd[5], "https://github.com/pallets/flask.git")
        self.assertEqual(cmd[6], str(path))

        env = mock_run.call_args[1].get("env", {})
        self.assertEqual(env.get("GIT_TERMINAL_PROMPT"), "0")
        self.assertEqual(env.get("GIT_CONFIG_COUNT"), "2")
        self.assertEqual(env.get("GIT_CONFIG_KEY_0"), "protocol.allow")
        self.assertEqual(env.get("GIT_CONFIG_VALUE_0"), "never")
        self.assertEqual(env.get("GIT_CONFIG_KEY_1"), "protocol.https.allow")
        self.assertEqual(env.get("GIT_CONFIG_VALUE_1"), "always")

        cleanup_repository(path)
        self.assertFalse(path.exists())

    def test_git_env_blocks_non_https_transport_in_git_cli(self):
        import shutil
        import tempfile
        from app.services.github_service import _build_git_env

        src = tempfile.mkdtemp()
        dst = tempfile.mkdtemp()
        try:
            subprocess.run(
                ["git", "init", "--bare", src],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            shutil.rmtree(dst)
            proc = subprocess.run(
                ["git", "clone", "--depth", "1", "--", f"file://{src}", dst],
                env=_build_git_env(),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("transport 'file' not allowed", proc.stderr)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(dst, ignore_errors=True)

    @patch("app.services.github_service.subprocess.run")
    def test_clone_timeout_handling_and_cleanup(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=5)

        with self.assertRaises(TimeoutError):
            clone_repository("https://github.com/pallets/flask", timeout_seconds=5)

    @patch("app.services.github_service.subprocess.run")
    def test_clone_process_error_handling_and_cleanup(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128, cmd="git", stderr=b"fatal: repo not found"
        )

        with self.assertRaises(ValueError):
            clone_repository("https://github.com/pallets/nonexistent", timeout_seconds=5)


if __name__ == "__main__":
    unittest.main()
