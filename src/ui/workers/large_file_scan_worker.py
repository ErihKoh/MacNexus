"""Фоновий потік пошуку великих файлів."""

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal
from src.services.large_file_scanner import LargeFileScanner


class LargeFileScanWorker(QThread):
    """Виконує пошук великих файлів у фоновому потоці."""

    scan_finished = Signal(list, bool)
    scan_error = Signal(str)

    def __init__(self, path: str | Path, min_size: int) -> None:
        super().__init__()

        self._path = Path(path)
        self._min_size = min_size
        self._scanner = LargeFileScanner()
        self._cancel_event = Event()

    def run(self) -> None:
        """Запускає пошук великих файлів."""

        try:
            entries = self._scanner.scan(
                self._path,
                min_size=self._min_size,
                should_cancel=self._cancel_event.is_set,
            )

            self.scan_finished.emit(entries, self._cancel_event.is_set())

        except (OSError, ValueError) as error:
            self.scan_error.emit(str(error))

    def cancel(self) -> None:
        """Надсилає запит на скасування сканування."""

        self._cancel_event.set()
