"""Тести сервісу пошуку великих файлів."""

import tempfile
import unittest
from pathlib import Path

from src.services.large_file_scanner import LargeFileScanner


class TestLargeFileScanner(unittest.TestCase):
    """Перевіряє пошук і фільтрацію великих файлів."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.scanner = LargeFileScanner()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_scan_returns_files_above_minimum_size(self) -> None:
        (self.root / "small.txt").write_bytes(b"a" * 100)
        (self.root / "medium.txt").write_bytes(b"b" * 500)
        (self.root / "large.txt").write_bytes(b"c" * 1000)

        results = self.scanner.scan(self.root, min_size=500)

        self.assertEqual(
            [entry.name for entry in results],
            ["large.txt", "medium.txt"],
        )

    def test_scan_sorts_files_by_size_descending(self) -> None:
        (self.root / "first.txt").write_bytes(b"a" * 300)
        (self.root / "second.txt").write_bytes(b"b" * 900)
        (self.root / "third.txt").write_bytes(b"c" * 600)

        results = self.scanner.scan(self.root, min_size=0)

        self.assertEqual(
            [entry.size for entry in results],
            [900, 600, 300],
        )

    def test_scan_includes_files_equal_to_minimum_size(self) -> None:
        (self.root / "exact.txt").write_bytes(b"a" * 500)

        results = self.scanner.scan(self.root, min_size=500)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].size, 500)

    def test_scan_returns_empty_list_when_no_files_match(self) -> None:
        (self.root / "small.txt").write_bytes(b"a" * 100)

        results = self.scanner.scan(self.root, min_size=1000)

        self.assertEqual(results, [])

    def test_scan_rejects_negative_minimum_size(self) -> None:
        with self.assertRaises(ValueError):
            self.scanner.scan(self.root, min_size=-1)

    def test_scan_supports_cancellation(self) -> None:
        (self.root / "file.txt").write_bytes(b"a" * 1000)

        results = self.scanner.scan(
            self.root,
            min_size=0,
            should_cancel=lambda: True,
        )

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
