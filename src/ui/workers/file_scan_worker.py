"""Фоновий потік пакетного сканування файлової системи."""

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal
from src.models.file_entry import FileEntry
from src.services.file_scanner import FileScanner


class FileScanWorker(QThread):
    """Виконує сканування та передає результати пакетами."""

    BATCH_SIZE = 500

    batch_found = Signal(list)
    scan_finished = Signal(int, int)
    scan_error = Signal(str)

    def __init__(self, path: str | Path) -> None:
        super().__init__()

        self._path = Path(path)
        self._scanner = FileScanner()
        self._cancel_event = Event()
        self._batch: list[FileEntry] = []

    def run(self) -> None:
        """Запускає потокове сканування."""

        try:
            file_count, total_size = self._scanner.scan_stream(
                self._path,
                should_cancel=self._cancel_event.is_set,
                on_file=self._collect_file,
            )

            self._emit_batch()
            self.scan_finished.emit(file_count, total_size)

        except (OSError, ValueError) as error:
            self._emit_batch()
            self.scan_error.emit(str(error))

    def cancel(self) -> None:
        """Надсилає запит на скасування сканування."""

        self._cancel_event.set()

    def _collect_file(self, entry: FileEntry) -> None:
        """Накопичує файли до формування пакета."""

        self._batch.append(entry)

        if len(self._batch) >= self.BATCH_SIZE:
            self._emit_batch()

    def _emit_batch(self) -> None:
        """Передає накопичений пакет до інтерфейсу."""

        if not self._batch:
            return

        batch = self._batch
        self._batch = []

        self.batch_found.emit(batch)
