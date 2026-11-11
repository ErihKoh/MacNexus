"""Тести моделі таблиці System Junk."""

import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication, Qt
from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult
from src.ui.models.junk_table_model import JunkTableModel


class TestJunkTableModel(unittest.TestCase):
    """Перевіряє JunkTableModel."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self) -> None:
        self.model = JunkTableModel()

        self.category = JunkCategory(
            name="User Caches",
            description="Кеші користувача",
            path=Path("/test/caches"),
        )

        self.result = JunkScanResult(
            category=self.category,
            file_count=10,
            total_size=1024,
        )

    def test_model_starts_empty(self) -> None:
        self.assertEqual(self.model.rowCount(), 0)
        self.assertEqual(self.model.columnCount(), 3)

    def test_set_results_updates_row_count(self) -> None:
        self.model.set_results([self.result])

        self.assertEqual(self.model.rowCount(), 1)

    def test_data_returns_category_name(self) -> None:
        self.model.set_results([self.result])

        index = self.model.index(0, 0)

        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole),
            "User Caches",
        )

    def test_data_returns_file_count(self) -> None:
        self.model.set_results([self.result])

        index = self.model.index(0, 1)

        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole),
            "10",
        )

    def test_data_returns_formatted_size(self) -> None:
        self.model.set_results([self.result])

        index = self.model.index(0, 2)

        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole),
            "1.0 KB",
        )

    def test_header_data_returns_column_names(self) -> None:
        expected = ["Категорія", "Файлів", "Розмір"]

        for column, header in enumerate(expected):
            self.assertEqual(
                self.model.headerData(
                    column,
                    Qt.Orientation.Horizontal,
                    Qt.ItemDataRole.DisplayRole,
                ),
                header,
            )

    def test_set_results_replaces_previous_results(self) -> None:
        self.model.set_results([self.result])
        self.model.set_results([])

        self.assertEqual(self.model.rowCount(), 0)


if __name__ == "__main__":
    unittest.main()
