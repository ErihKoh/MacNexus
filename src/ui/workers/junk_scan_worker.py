"""Фоновий потік сканування системного сміття."""

from threading import Event

from PySide6.QtCore import QThread, Signal
from src.models.junk_scan_result import JunkScanResult
from src.services.junk_service import JunkService


class JunkScanWorker(QThread):
    """Сканує категорії системного сміття у фоновому потоці."""

    category_scanned = Signal(object)
    scan_finished = Signal(list)
    scan_error = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._service = JunkService()
        self._cancel_event = Event()

    def run(self) -> None:
        """Послідовно сканує всі категорії."""

        results: list[JunkScanResult] = []

        try:
            categories = self._service.get_categories()

            for category in categories:
                if self._cancel_event.is_set():
                    break

                result = self._service.scan_category(
                    category,
                    should_cancel=self._cancel_event.is_set,
                )

                results.append(result)
                self.category_scanned.emit(result)

                if self._cancel_event.is_set():
                    break

            self.scan_finished.emit(results)

        except (OSError, ValueError) as error:
            self.scan_error.emit(str(error))

    def cancel(self) -> None:
        """Надсилає запит на скасування сканування."""

        self._cancel_event.set()
