"""Тести фонового потоку пошуку великих файлів."""

import tempfile
import time
import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy
from src.ui.workers.large_file_scan_worker import LargeFileScanWorker


class TestLargeFileScanWorker(unittest.TestCase):
    """Перевіряє роботу LargeFileScanWorker."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _run_worker(self, worker: LargeFileScanWorker) -> None:
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

    def test_worker_finds_large_files(self) -> None:
        """Перевіряє пошук великих файлів."""

        (self.root / "small.txt").write_bytes(b"a" * 100)
        (self.root / "large.txt").write_bytes(b"b" * 1000)

        worker = LargeFileScanWorker(self.root, min_size=500)
        finished_spy = QSignalSpy(worker.scan_finished)
        error_spy = QSignalSpy(worker.scan_error)

        self._run_worker(worker)

        self.assertEqual(error_spy.count(), 0)
        self.assertEqual(finished_spy.count(), 1)

        entries, cancelled = finished_spy.at(0)

        self.assertEqual([entry.name for entry in entries], ["large.txt"])
        self.assertFalse(cancelled)

    def test_worker_reports_invalid_path(self) -> None:
        """Перевіряє передавання помилки."""

        worker = LargeFileScanWorker(self.root / "missing", min_size=500)
        error_spy = QSignalSpy(worker.scan_error)

        self._run_worker(worker)

        self.assertEqual(error_spy.count(), 1)
        self.assertIn("Каталог не знайдено", error_spy.at(0)[0])

    def test_worker_reports_cancellation(self) -> None:
        """Перевіряє скасування до початку сканування."""

        (self.root / "large.txt").write_bytes(b"a" * 1000)

        worker = LargeFileScanWorker(self.root, min_size=500)
        finished_spy = QSignalSpy(worker.scan_finished)

        worker.cancel()
        self._run_worker(worker)

        self.assertEqual(finished_spy.count(), 1)

        entries, cancelled = finished_spy.at(0)

        self.assertTrue(cancelled)
        self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
