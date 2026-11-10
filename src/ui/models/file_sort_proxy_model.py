
"""Проксі-модель для сортування таблиці файлів."""

from PySide6.QtCore import QSortFilterProxyModel, Qt


class FileSortProxyModel(QSortFilterProxyModel):
    """Забезпечує сортування файлів без зміни вихідної моделі."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSortRole(Qt.ItemDataRole.UserRole)
        self.setDynamicSortFilter(True)
