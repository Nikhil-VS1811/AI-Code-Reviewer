import tempfile
import time
import unittest
from pathlib import Path

from app.services.repository_scanner import (
    collect_source_files,
    MAX_FILES,
    MAX_FILE_SIZE_BYTES,
)


class TestRepositoryScannerLimits(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_collect_files_capped_at_max_files(self):
        # Create 600 small python files
        for i in range(600):
            p = self.root_path / f"test_file_{i:04d}.py"
            p.write_text("x = 1\n", encoding="utf-8")

        collected = collect_source_files(self.root_path, max_files=500)
        self.assertEqual(len(collected), 500)

    def test_collect_files_skips_files_exceeding_max_size(self):
        small_file = self.root_path / "small.py"
        small_file.write_text("a = 1\n", encoding="utf-8")

        # Create oversized file (>500KB)
        large_file = self.root_path / "large.py"
        large_file.write_bytes(b"x" * (MAX_FILE_SIZE_BYTES + 1024))

        collected = collect_source_files(
            self.root_path,
            max_file_size_bytes=MAX_FILE_SIZE_BYTES,
        )
        self.assertIn(small_file, collected)
        self.assertNotIn(large_file, collected)

    def test_collect_files_respects_deadline(self):
        # Create 100 files
        for i in range(100):
            p = self.root_path / f"test_{i}.py"
            p.write_text("y = 2\n", encoding="utf-8")

        # Passing 0 or near-zero deadline should terminate immediately
        collected = collect_source_files(self.root_path, deadline_seconds=0.0)
        self.assertEqual(len(collected), 0)


if __name__ == "__main__":
    unittest.main()
