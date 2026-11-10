"""Тести сортування таблиці файлів."""

import unittest
from pathlib import Path

from PySide6.QtCore import Qt
from src.models.file_entry import FileEntry
from src.ui.models.file_sort_proxy_model import FileSortProxyModel
from src.ui.models.file_table_model import FileTableModel


class TestFileSortProxyModel(unittest.TestCase):
    """Перевіряє сортування файлів за різними параметрами."""

    def setUp(self) -> None:
        self.model = FileTableModel()

        self.model.append_entries(
            [
                FileEntry(
                    Path("/Users/test/zebra.txt"),
                    "zebra.txt",
                    100,
                    1700000000.0,
                ),
                FileEntry(
                    Path("/Users/test/Apple.txt"),
                    "Apple.txt",
                    2048,
                    1600000000.0,
                ),
                FileEntry(
                    Path("/Users/test/banana.txt"),
                    "banana.txt",
                    512,
                    1800000000.0,
                ),
            ]
        )

        self.proxy = FileSortProxyModel()
        self.proxy.setSourceModel(self.model)

    def sorted_values(
        self,
        column: int,
        order: Qt.SortOrder = Qt.SortOrder.AscendingOrder,
    ) -> list:
        """Повертає значення стовпця після сортування."""

        self.proxy.sort(column, order)

        return [
            self.proxy.index(row, column).data(Qt.ItemDataRole.UserRole)
            for row in range(self.proxy.rowCount())
        ]

    def test_sort_by_name(self) -> None:
        """Перевіряє сортування за назвою."""

        self.assertEqual(
            self.sorted_values(0),
            ["apple.txt", "banana.txt", "zebra.txt"],
        )

    def test_sort_by_size(self) -> None:
        """Перевіряє числове сортування розміру."""

        self.assertEqual(
            self.sorted_values(1),
            [100, 512, 2048],
        )

    def test_sort_by_date(self) -> None:
        """Перевіряє сортування за датою."""

        self.assertEqual(
            self.sorted_values(2),
            [1600000000.0, 1700000000.0, 1800000000.0],
        )

    def test_sort_by_path(self) -> None:
        """Перевіряє сортування за шляхом."""

        self.assertEqual(
            self.sorted_values(3),
            [
                "/users/test/apple.txt",
                "/users/test/banana.txt",
                "/users/test/zebra.txt",
            ],
        )

    def test_sort_descending(self) -> None:
        """Перевіряє сортування у зворотному порядку."""

        self.assertEqual(
            self.sorted_values(1, Qt.SortOrder.DescendingOrder),
            [2048, 512, 100],
        )


if __name__ == "__main__":
    unittest.main()
