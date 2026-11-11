"""Модель таблиці результатів System Junk."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from src.models.junk_scan_result import JunkScanResult

_INVALID_INDEX = QModelIndex()


class JunkTableModel(QAbstractTableModel):
    """Відображає результати сканування системного сміття."""

    HEADERS = ("Категорія", "Файлів", "Розмір")

    def __init__(self) -> None:
        super().__init__()

        self._results: list[JunkScanResult] = []

    def rowCount(self, parent: QModelIndex = _INVALID_INDEX) -> int:
        if parent.isValid():
            return 0

        return len(self._results)

    def columnCount(self, parent: QModelIndex = _INVALID_INDEX) -> int:
        if parent.isValid():
            return 0

        return len(self.HEADERS)

    def data(
        self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        result = self._results[index.row()]

        if index.column() == 0:
            return result.category.name

        if index.column() == 1:
            return str(result.file_count)

        if index.column() == 2:
            return self._format_size(result.total_size)

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]

        return None

    def set_results(self, results: list[JunkScanResult]) -> None:
        """Замінює результати таблиці."""

        self.beginResetModel()
        self._results = results.copy()
        self.endResetModel()

    def _format_size(self, size: int) -> str:
        """Форматує розмір файлів."""

        units = ("B", "KB", "MB", "GB", "TB")
        value = float(size)

        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} TB"
