"""Тести пакетного фонового сканування."""

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

    def test_worker_returns_files_in_batches(self) -> None:
        """Перевіряє пакетне передавання файлів."""

        (self.root / "document.txt").write_text("MacNexus", encoding="utf-8")

        worker = FileScanWorker(self.root)
        batch_spy = QSignalSpy(worker.batch_found)
        finished_spy = QSignalSpy(worker.scan_finished)

        self._run_worker(worker)

        self.assertEqual(batch_spy.count(), 1)
        self.assertEqual(len(batch_spy.at(0)[0]), 1)

        self.assertEqual(finished_spy.count(), 1)
        self.assertEqual(finished_spy.at(0), [1, 8])

    def test_worker_splits_large_scan_into_batches(self) -> None:
        """Перевіряє розбиття результатів на пакети."""

        file_count = FileScanWorker.BATCH_SIZE + 10

        for index in range(file_count):
            (self.root / f"file_{index}.txt").touch()

        worker = FileScanWorker(self.root)
        batch_spy = QSignalSpy(worker.batch_found)

        self._run_worker(worker)

        self.assertEqual(batch_spy.count(), 2)
        self.assertEqual(len(batch_spy.at(0)[0]), 500)
        self.assertEqual(len(batch_spy.at(1)[0]), 10)

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
        batch_spy = QSignalSpy(worker.batch_found)
        finished_spy = QSignalSpy(worker.scan_finished)

        worker.cancel()
        self._run_worker(worker)

        self.assertEqual(finished_spy.count(), 1)
        self.assertEqual(finished_spy.at(0), [0, 0])
        self.assertEqual(batch_spy.count(), 0)


if __name__ == "__main__":
    unittest.main()
