"""Модель таблиці директорій Disk Analyzer."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from src.models.directory_entry import DirectoryEntry


class DirectoryTableModel(QAbstractTableModel):
    """Зберігає та надає статистику директорій для QTableView."""

    HEADERS = ("Назва", "Розмір", "Кількість файлів", "Шлях")

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[DirectoryEntry] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._entries)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._entries):
            return None

        entry = self._entries[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            values = (
                entry.name,
                self._format_size(entry.size),
                str(entry.file_count),
                str(entry.path),
            )
            return values[index.column()] if 0 <= index.column() < len(values) else None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() in (1, 2):
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and 0 <= section < len(self.HEADERS)
        ):
            return self.HEADERS[section]

        return None

    def replace_entries(self, entries: list[DirectoryEntry]) -> None:
        """Замінює записи директорій."""

        self.beginResetModel()
        self._entries = entries
        self.endResetModel()

    def clear(self) -> None:
        """Очищає таблицю."""

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
