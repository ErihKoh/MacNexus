"""Тести моделі результатів сканування."""

import unittest
from pathlib import Path

from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult


class TestJunkScanResult(unittest.TestCase):
    """Перевіряє JunkScanResult."""

    def test_result_stores_values(self) -> None:
        category = JunkCategory(
            name="User Caches",
            description="Кеші програм",
            path=Path.home() / "Library" / "Caches",
        )

        result = JunkScanResult(
            category=category,
            file_count=10,
            total_size=1024,
        )

        self.assertEqual(result.category, category)
        self.assertEqual(result.file_count, 10)
        self.assertEqual(result.total_size, 1024)

    def test_result_is_immutable(self) -> None:
        category = JunkCategory(
            name="Logs",
            description="Журнали",
            path=Path.home() / "Library" / "Logs",
        )

        result = JunkScanResult(
            category=category,
            file_count=5,
            total_size=512,
        )

        with self.assertRaises(AttributeError):
            result.total_size = 100  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
