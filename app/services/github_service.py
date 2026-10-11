import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# Strict HTTPS GitHub repository URL format
GITHUB_REPO_REGEX = re.compile(
    r"^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$"
)

CLONE_TIMEOUT_SECONDS = 60


def _build_git_env() -> dict[str, str]:
    """Build a hardened Git subprocess environment.

    - Disables interactive credential prompts so clones never hang on private repos.
    - Restricts Git transport protocols strictly to HTTPS so redirects cannot
      downgrade or switch to file://, ssh://, git://, or http:// transports.
    """
    env = os.environ.copy()
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "protocol.allow",
            "GIT_CONFIG_VALUE_0": "never",
            "GIT_CONFIG_KEY_1": "protocol.https.allow",
            "GIT_CONFIG_VALUE_1": "always",
        }
    )
    return env


def validate_github_url(repo_url: str) -> str:
    """
    Validates that a URL is a legitimate HTTPS GitHub repository URL.
    Rejects flag injection, non-HTTPS protocols, SSRF targets, and malicious formatting.
    Returns normalized canonical URL.
    """
    if not isinstance(repo_url, str):
        raise ValueError("Repository URL must be a string.")

    cleaned_url = repo_url.strip()

    # Reject arguments starting with hyphen to prevent Git option/flag injection
    if cleaned_url.startswith("-"):
        raise ValueError("Invalid repository URL format.")

    match = GITHUB_REPO_REGEX.match(cleaned_url)
    if not match:
        raise ValueError(
            "Invalid GitHub repository URL. Must be an HTTPS GitHub URL (e.g. https://github.com/owner/repo)."
        )

    owner, repo = match.groups()

    # Disallow reserved or traversal path segments
    if owner in {".", ".."} or repo in {".", ".."}:
        raise ValueError("Invalid repository path.")

    return f"https://github.com/{owner}/{repo}.git"


def clone_repository(repo_url: str, timeout_seconds: int = CLONE_TIMEOUT_SECONDS) -> Path:
    normalized_url = validate_github_url(repo_url)
    temp_dir = tempfile.mkdtemp(prefix="ai_review_repo_")

    try:
        # Use '--' to separate git clone flags from positional URL and destination operands
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--",
                normalized_url,
                str(temp_dir),
            ],
            check=True,
            timeout=timeout_seconds,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=_build_git_env(),
        )
        return Path(temp_dir)
    except subprocess.TimeoutExpired as exc:
        cleanup_repository(Path(temp_dir))
        raise TimeoutError(
            f"Repository cloning timed out after {timeout_seconds} seconds."
        ) from exc
    except subprocess.CalledProcessError as exc:
        cleanup_repository(Path(temp_dir))
        raise ValueError(
            "Failed to clone repository. Please verify that the repository exists, is public, and is accessible."
        ) from exc
    except Exception:
        cleanup_repository(Path(temp_dir))
        raise


def cleanup_repository(repo_path: Path):
    if repo_path and isinstance(repo_path, Path) and repo_path.exists():
        shutil.rmtree(repo_path, ignore_errors=True)