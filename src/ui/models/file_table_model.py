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
        self._path_sort_keys: list[str] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        """Повертає кількість файлів."""

        if parent is not None and parent.isValid():
            return 0

        return len(self._entries)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        """Повертає кількість стовпців."""

        if parent is not None and parent.isValid():
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

        if not (0 <= index.row() < len(self._entries)):
            return None

        if not (0 <= index.column() < len(self.HEADERS)):
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
            if column == 0:
                return entry.name.casefold()
            if column == 1:
                return entry.size
            if column == 2:
                return entry.modified_at
            if column == 3:
                return self._path_sort_keys[index.row()]

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
        self._path_sort_keys.extend(str(entry.path).casefold() for entry in entries)
        self.endInsertRows()

    def entries_snapshot(self) -> list[FileEntry]:
        """Повертає копію списку записів для фонового оброблення."""

        return self._entries.copy()

    def replace_entries(self, entries: list[FileEntry]) -> None:
        """Замінює записи моделі готовим списком файлів."""

        self.beginResetModel()

        self._entries = entries
        self._path_sort_keys = [str(entry.path).casefold() for entry in entries]

        self.endResetModel()

    def entry_at(self, row: int) -> FileEntry | None:
        """Повертає запис за індексом рядка."""

        if 0 <= row < len(self._entries):
            return self._entries[row]

        return None

    def clear(self) -> None:
        """Очищає модель."""

        if not self._entries:
            return

        self.beginResetModel()
        self._entries.clear()
        self._path_sort_keys.clear()
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
