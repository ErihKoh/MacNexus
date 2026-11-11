"""Тести фонового сканування системного сміття."""

import time
import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy
from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult
from src.ui.workers.junk_scan_worker import JunkScanWorker


class FakeJunkService:
    """Тестовий сервіс сканування."""

    def __init__(self) -> None:
        self.categories = [
            JunkCategory("Caches", "Кеші", Path("/test/caches")),
            JunkCategory("Logs", "Журнали", Path("/test/logs")),
        ]

    def get_categories(self) -> list[JunkCategory]:
        return self.categories

    def scan_category(
        self,
        category: JunkCategory,
        should_cancel=None,
    ) -> JunkScanResult:
        return JunkScanResult(
            category=category,
            file_count=2,
            total_size=1024,
        )


class FailingJunkService:
    """Тестовий сервіс, який генерує помилку."""

    def get_categories(self) -> list[JunkCategory]:
        raise OSError("Test error")


class TestJunkScanWorker(unittest.TestCase):
    """Перевіряє JunkScanWorker."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def _run_worker(self, worker: JunkScanWorker) -> None:
        """Запускає потік і очікує його завершення."""

        finished_spy = QSignalSpy(worker.finished)

        worker.start()

        deadline = time.monotonic() + 5

        while finished_spy.count() == 0 and time.monotonic() < deadline:
            finished_spy.wait(100)

        if not worker.wait(1000):
            worker.cancel()
            worker.wait(5000)

        self.assertEqual(finished_spy.count(), 1)
        self.assertFalse(worker.isRunning())

    def test_worker_scans_categories(self) -> None:
        """Перевіряє сканування та передавання результатів."""

        worker = JunkScanWorker()
        worker._service = FakeJunkService()

        category_spy = QSignalSpy(worker.category_scanned)
        finished_spy = QSignalSpy(worker.scan_finished)

        self._run_worker(worker)

        self.assertEqual(category_spy.count(), 2)
        self.assertEqual(finished_spy.count(), 1)

        results = finished_spy.at(0)[0]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].file_count, 2)
        self.assertEqual(results[0].total_size, 1024)

    def test_worker_can_be_cancelled(self) -> None:
        """Перевіряє скасування до початку сканування."""

        worker = JunkScanWorker()
        worker._service = FakeJunkService()

        category_spy = QSignalSpy(worker.category_scanned)
        finished_spy = QSignalSpy(worker.scan_finished)

        worker.cancel()
        self._run_worker(worker)

        self.assertEqual(category_spy.count(), 0)
        self.assertEqual(finished_spy.count(), 1)
        self.assertEqual(finished_spy.at(0)[0], [])

    def test_worker_reports_error(self) -> None:
        """Перевіряє передавання помилки сервісу."""

        worker = JunkScanWorker()
        worker._service = FailingJunkService()

        error_spy = QSignalSpy(worker.scan_error)

        self._run_worker(worker)

        self.assertEqual(error_spy.count(), 1)
        self.assertIn("Test error", error_spy.at(0)[0])


if __name__ == "__main__":
    unittest.main()
