"""Тести сервісу сканування файлової системи."""

import tempfile
import unittest
from pathlib import Path

from src.services.file_scanner import FileScanner


class TestFileScanner(unittest.TestCase):
    """Перевіряє роботу FileScanner."""

    def setUp(self) -> None:
        self.scanner = FileScanner()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_scan_returns_files(self) -> None:
        """Перевіряє пошук файлів у каталозі."""

        file_path = self.root / "document.txt"
        file_path.write_text("Hello MacNexus", encoding="utf-8")

        result = self.scanner.scan(self.root)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "document.txt")
        self.assertEqual(result[0].size, 14)
        self.assertEqual(result[0].path, file_path)

    def test_scan_finds_files_in_subdirectories(self) -> None:
        """Перевіряє рекурсивне сканування."""

        nested_dir = self.root / "documents"
        nested_dir.mkdir()

        (nested_dir / "report.pdf").write_bytes(b"PDF")
        (self.root / "image.png").write_bytes(b"PNG")

        result = self.scanner.scan(self.root)

        self.assertEqual(len(result), 2)

        names = {entry.name for entry in result}

        self.assertEqual(names, {"report.pdf", "image.png"})

    def test_scan_returns_empty_list_for_empty_directory(self) -> None:
        """Перевіряє порожній каталог."""

        result = self.scanner.scan(self.root)

        self.assertEqual(result, [])

    def test_scan_raises_error_for_missing_directory(self) -> None:
        """Перевіряє обробку неіснуючого каталогу."""

        missing_path = self.root / "missing"

        with self.assertRaises(FileNotFoundError):
            self.scanner.scan(missing_path)

    def test_scan_raises_error_for_file_path(self) -> None:
        """Перевіряє передачу шляху до файлу замість каталогу."""

        file_path = self.root / "document.txt"
        file_path.write_text("Test", encoding="utf-8")

        with self.assertRaises(NotADirectoryError):
            self.scanner.scan(file_path)

    def test_scan_does_not_follow_symlinks(self) -> None:
        """Перевіряє пропуск символічних посилань."""

        target = self.root / "target.txt"
        target.write_text("Target", encoding="utf-8")

        link = self.root / "link.txt"

        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("Створення символічних посилань недоступне.")

        result = self.scanner.scan(self.root)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "target.txt")


if __name__ == "__main__":
    unittest.main()
