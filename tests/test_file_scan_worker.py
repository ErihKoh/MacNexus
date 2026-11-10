"""Тести фонового сканування файлової системи."""

import tempfile
import time
import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy
from src.ui.workers.file_scan_worker import FileScanWorker


class TestFileScanWorker(unittest.TestCase):
    """Перевіряє роботу FileScanWorker."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _run_worker(self, worker: FileScanWorker) -> None:
        """Запускає потік і надійно очікує його завершення."""

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

    def test_worker_returns_scan_results(self) -> None:
        """Перевіряє передавання знайдених файлів."""

        file_path = self.root / "document.txt"
        file_path.write_text("MacNexus", encoding="utf-8")

        worker = FileScanWorker(self.root)
        found_spy = QSignalSpy(worker.file_found)
        finished_spy = QSignalSpy(worker.scan_finished)

        self._run_worker(worker)

        self.assertEqual(found_spy.count(), 1)
        self.assertEqual(finished_spy.count(), 1)
        self.assertEqual(len(finished_spy.at(0)[0]), 1)
        self.assertEqual(finished_spy.at(0)[0][0].name, "document.txt")

    def test_worker_reports_error_for_missing_directory(self) -> None:
        """Перевіряє передавання помилки."""

        worker = FileScanWorker(self.root / "missing")
        error_spy = QSignalSpy(worker.scan_error)

        self._run_worker(worker)

        self.assertEqual(error_spy.count(), 1)
        self.assertIn("Каталог не знайдено", error_spy.at(0)[0])

    def test_worker_can_be_cancelled(self) -> None:
        """Перевіряє скасування до початку сканування."""

        (self.root / "document.txt").write_text("Test", encoding="utf-8")

        worker = FileScanWorker(self.root)
        finished_spy = QSignalSpy(worker.scan_finished)

        worker.cancel()
        self._run_worker(worker)

        self.assertEqual(finished_spy.count(), 1)
        self.assertEqual(finished_spy.at(0)[0], [])

    def test_worker_emits_file_found_signal(self) -> None:
        """Перевіряє сигнал про знайдений файл."""

        (self.root / "first.txt").write_text("First", encoding="utf-8")
        (self.root / "second.txt").write_text("Second", encoding="utf-8")

        worker = FileScanWorker(self.root)
        found_spy = QSignalSpy(worker.file_found)

        self._run_worker(worker)

        self.assertEqual(found_spy.count(), 2)


if __name__ == "__main__":
    unittest.main()
