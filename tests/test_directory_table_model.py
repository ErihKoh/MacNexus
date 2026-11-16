"""Тести моделі таблиці директорій."""

import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication, Qt
from src.models.directory_entry import DirectoryEntry
from src.ui.models.directory_table_model import DirectoryTableModel


class TestDirectoryTableModel(unittest.TestCase):
    """Перевіряє DirectoryTableModel."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self) -> None:
        self.model = DirectoryTableModel()

        self.entry = DirectoryEntry(
            path=Path("/test/documents"),
            name="documents",
            size=2048,
            file_count=15,
        )

    def test_model_starts_empty(self) -> None:
        self.assertEqual(self.model.rowCount(), 0)
        self.assertEqual(self.model.columnCount(), 4)

    def test_replace_entries_updates_row_count(self) -> None:
        self.model.replace_entries([self.entry])

        self.assertEqual(self.model.rowCount(), 1)

    def test_data_returns_directory_name(self) -> None:
        self.model.replace_entries([self.entry])

        self.assertEqual(
            self.model.data(self.model.index(0, 0)),
            "documents",
        )

    def test_data_returns_formatted_size(self) -> None:
        self.model.replace_entries([self.entry])

        self.assertEqual(
            self.model.data(self.model.index(0, 1)),
            "2.0 KB",
        )

    def test_data_returns_file_count(self) -> None:
        self.model.replace_entries([self.entry])

        self.assertEqual(
            self.model.data(self.model.index(0, 2)),
            "15",
        )

    def test_data_returns_directory_path(self) -> None:
        self.model.replace_entries([self.entry])

        self.assertEqual(
            self.model.data(self.model.index(0, 3)),
            "/test/documents",
        )

    def test_header_data_returns_column_names(self) -> None:
        expected = ["Назва", "Розмір", "Кількість файлів", "Шлях"]

        for column, header in enumerate(expected):
            self.assertEqual(
                self.model.headerData(
                    column,
                    Qt.Orientation.Horizontal,
                    Qt.ItemDataRole.DisplayRole,
                ),
                header,
            )

    def test_replace_entries_replaces_previous_entries(self) -> None:
        self.model.replace_entries([self.entry])
        self.model.replace_entries([])

        self.assertEqual(self.model.rowCount(), 0)

    def test_clear_removes_all_entries(self) -> None:
        self.model.replace_entries([self.entry])
        self.model.clear()

        self.assertEqual(self.model.rowCount(), 0)


if __name__ == "__main__":
    unittest.main()
