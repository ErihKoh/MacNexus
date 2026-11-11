"""Тести сервісу визначення та сканування системного сміття."""

import tempfile
import unittest
from pathlib import Path

from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult
from src.services.junk_service import JunkService


class TestJunkService(unittest.TestCase):
    """Перевіряє JunkService."""

    def setUp(self) -> None:
        self.service = JunkService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_get_categories_returns_three_categories(self) -> None:
        categories = self.service.get_categories()

        self.assertEqual(len(categories), 3)

    def test_get_categories_returns_expected_names(self) -> None:
        categories = self.service.get_categories()

        names = [category.name for category in categories]

        self.assertEqual(
            names,
            ["User Caches", "Logs", "Trash"],
        )

    def test_get_categories_returns_expected_paths(self) -> None:
        library = Path.home() / "Library"

        categories = self.service.get_categories()

        paths = [category.path for category in categories]

        self.assertEqual(
            paths,
            [
                library / "Caches",
                library / "Logs",
                Path.home() / ".Trash",
            ],
        )

    def test_categories_are_junk_category_instances(self) -> None:
        categories = self.service.get_categories()

        for category in categories:
            with self.subTest(category=category.name):
                self.assertIsInstance(category.path, Path)
                self.assertTrue(category.description)

    def test_scan_category_counts_files_and_size(self) -> None:
        (self.root / "small.txt").write_bytes(b"a" * 10)
        (self.root / "large.txt").write_bytes(b"b" * 100)

        category = JunkCategory(
            name="Test",
            description="Тестова категорія",
            path=self.root,
        )

        result = self.service.scan_category(category)

        self.assertIsInstance(result, JunkScanResult)
        self.assertEqual(result.category, category)
        self.assertEqual(result.file_count, 2)
        self.assertEqual(result.total_size, 110)

    def test_scan_category_finds_nested_files(self) -> None:
        nested = self.root / "nested"
        nested.mkdir()

        (nested / "file.txt").write_bytes(b"test")

        category = JunkCategory(
            name="Test",
            description="Тестова категорія",
            path=self.root,
        )

        result = self.service.scan_category(category)

        self.assertEqual(result.file_count, 1)
        self.assertEqual(result.total_size, 4)

    def test_scan_category_returns_zero_for_missing_path(self) -> None:
        category = JunkCategory(
            name="Missing",
            description="Відсутній каталог",
            path=self.root / "missing",
        )

        result = self.service.scan_category(category)

        self.assertEqual(result.file_count, 0)
        self.assertEqual(result.total_size, 0)

    def test_scan_category_supports_cancellation(self) -> None:
        (self.root / "file.txt").write_bytes(b"test")

        category = JunkCategory(
            name="Test",
            description="Тестова категорія",
            path=self.root,
        )

        result = self.service.scan_category(
            category,
            should_cancel=lambda: True,
        )

        self.assertEqual(result.file_count, 0)
        self.assertEqual(result.total_size, 0)


if __name__ == "__main__":
    unittest.main()
