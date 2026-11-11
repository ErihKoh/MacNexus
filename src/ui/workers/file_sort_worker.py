"""Фоновий потік сортування файлів за розміром."""

from PySide6.QtCore import QThread, Signal
from src.models.file_entry import FileEntry


class FileSortWorker(QThread):
    """Сортує файли від найбільшого до найменшого."""

    sorting_finished = Signal(list)

    def __init__(self, entries: list[FileEntry]) -> None:
        super().__init__()
        self._entries = entries

    def run(self) -> None:
        """Виконує сортування у фоновому потоці."""

        sorted_entries = sorted(
            self._entries,
            key=lambda entry: entry.size,
            reverse=True,
        )

        self.sorting_finished.emit(sorted_entries)
