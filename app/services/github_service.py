import shutil
import subprocess
import tempfile
from pathlib import Path


def clone_repository(repo_url: str) -> Path:
    temp_dir = tempfile.mkdtemp()

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, temp_dir],
        check=True,
    )

    return Path(temp_dir)


def cleanup_repository(repo_path: Path):
    shutil.rmtree(repo_path, ignore_errors=True)