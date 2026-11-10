"""Модель таблиці файлів Disk Analyzer."""

from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from src.models.file_entry import FileEntry


class FileTableModel(QAbstractTableModel):
    """Зберігає та надає дані файлів для QTableView."""

    HEADERS = ("Назва", "Розмір", "Змінено", "Шлях")

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[FileEntry] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Повертає кількість файлів."""

        if parent.isValid():
            return 0

        return len(self._entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Повертає кількість стовпців."""

        if parent.isValid():
            return 0

        return len(self.HEADERS)

    def data(
        self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | int | float | None:
        """Повертає значення комірки."""

        if not index.isValid():
            return None

        entry = self._entries[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return entry.name

            if column == 1:
                return self._format_size(entry.size)

            if column == 2:
                return datetime.fromtimestamp(entry.modified_at).strftime("%Y-%m-%d %H:%M")

            if column == 3:
                return str(entry.path)

        if role == Qt.ItemDataRole.UserRole:
            values = (
                entry.name.casefold(),
                entry.size,
                entry.modified_at,
                str(entry.path).casefold(),
            )
            return values[column]

        if role == Qt.ItemDataRole.TextAlignmentRole and column == 1:
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        """Повертає назви стовпців."""

        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and 0 <= section < len(self.HEADERS)
        ):
            return self.HEADERS[section]

        return None

    def append_entries(self, entries: list[FileEntry]) -> None:
        """Додає пакет файлів до моделі."""

        if not entries:
            return

        first_row = len(self._entries)
        last_row = first_row + len(entries) - 1

        self.beginInsertRows(QModelIndex(), first_row, last_row)
        self._entries.extend(entries)
        self.endInsertRows()

    def entries(self) -> list[FileEntry]:
        """Повертає копію списку файлів."""

        return self._entries.copy()

    def clear(self) -> None:
        """Очищає модель."""

        if not self._entries:
            return

        self.beginResetModel()
        self._entries.clear()
        self.endResetModel()

    @staticmethod
    def _format_size(size: int) -> str:
        """Перетворює байти у зручний формат."""

        value = float(size)

        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} TB"
