"""Елемент таблиці з підтримкою сортування за вихідним значенням."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class SortableTableWidgetItem(QTableWidgetItem):
    """Порівнює елементи за значенням, а не за відображуваним текстом."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        """Порівнює два елементи таблиці."""

        self_value = self.data(Qt.ItemDataRole.UserRole)
        other_value = other.data(Qt.ItemDataRole.UserRole)

        if self_value is None or other_value is None:
            return self.text().casefold() < other.text().casefold()

        return self_value < other_value
