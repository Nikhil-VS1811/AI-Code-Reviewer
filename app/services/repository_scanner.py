import os
from pathlib import Path


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


def collect_source_files(repo_path: Path):
    files = []

    for root, directories, filenames in os.walk(repo_path):
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        root_path = Path(root)
        for filename in filenames:
            file = root_path / filename
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(file)

    return files
