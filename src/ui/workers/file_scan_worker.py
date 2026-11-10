"""Фоновий потік сканування файлової системи."""

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal
from src.models.file_entry import FileEntry
from src.services.file_scanner import FileScanner


class FileScanWorker(QThread):
    """Виконує сканування без блокування інтерфейсу."""

    file_found = Signal(object)
    scan_finished = Signal(list)
    scan_error = Signal(str)

    def __init__(self, path: str | Path) -> None:
        super().__init__()

        self._path = Path(path)
        self._scanner = FileScanner()
        self._cancel_event = Event()

    def run(self) -> None:
        """Запускає сканування у фоновому потоці."""

        try:
            results = self._scanner.scan(
                self._path,
                should_cancel=self._cancel_event.is_set,
                on_file=self._emit_file,
            )

            self.scan_finished.emit(results)

        except (OSError, ValueError) as error:
            self.scan_error.emit(str(error))

    def cancel(self) -> None:
        """Надсилає запит на скасування сканування."""

        self._cancel_event.set()

    def _emit_file(self, entry: FileEntry) -> None:
        """Передає знайдений файл до інтерфейсу."""

        self.file_found.emit(entry)
