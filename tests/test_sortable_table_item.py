"""Тести сортування елементів таблиці."""

import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.ui.widgets.sortable_table_item import SortableTableWidgetItem


class TestSortableTableWidgetItem(unittest.TestCase):
    """Перевіряє порівняння елементів таблиці."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_numeric_sorting(self) -> None:
        """Перевіряє числове сортування розмірів."""

        small = SortableTableWidgetItem("900 KB")
        large = SortableTableWidgetItem("1.2 MB")

        small.setData(Qt.ItemDataRole.UserRole, 900 * 1024)
        large.setData(Qt.ItemDataRole.UserRole, 1_200_000)

        self.assertLess(small, large)

    def test_date_sorting(self) -> None:
        """Перевіряє хронологічне сортування."""

        older = SortableTableWidgetItem("2026-01-01")
        newer = SortableTableWidgetItem("2026-11-01")

        older.setData(Qt.ItemDataRole.UserRole, 1767225600.0)
        newer.setData(Qt.ItemDataRole.UserRole, 1793491200.0)

        self.assertLess(older, newer)

    def test_text_sorting(self) -> None:
        """Перевіряє сортування тексту без урахування регістру."""

        first = SortableTableWidgetItem("Applications")
        second = SortableTableWidgetItem("System")

        first.setData(Qt.ItemDataRole.UserRole, "applications")
        second.setData(Qt.ItemDataRole.UserRole, "system")

        self.assertLess(first, second)


if __name__ == "__main__":
    unittest.main()
