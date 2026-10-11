import os
import time
from pathlib import Path


MAX_FILES = 500
MAX_FILE_SIZE_BYTES = 500 * 1024  # 500 KB per file
DEFAULT_SCAN_DEADLINE_SECONDS = 30.0

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "venv",
    ".venv",
    "__pycache__",
}

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".h",
}
EXTENSION_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "cpp",
    ".h": "cpp",
}


def collect_source_files(
    repo_path: Path,
    max_files: int = MAX_FILES,
    max_file_size_bytes: int = MAX_FILE_SIZE_BYTES,
    deadline_seconds: float = DEFAULT_SCAN_DEADLINE_SECONDS,
) -> list[Path]:
    files = []
    start_time = time.monotonic()
    deadline = start_time + deadline_seconds

    for root, directories, filenames in os.walk(repo_path):
        if time.monotonic() > deadline:
            break

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        root_path = Path(root)
        for filename in sorted(filenames):
            if time.monotonic() > deadline:
                break

            file = root_path / filename
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    file_size = file.stat().st_size
                    if file_size <= max_file_size_bytes:
                        files.append(file)
                        if len(files) >= max_files:
                            return files
                except OSError:
                    continue

    return files
