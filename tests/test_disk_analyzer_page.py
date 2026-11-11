"""Тести сторінки аналізу диска."""

import tempfile
import unittest
from pathlib import Path

from PySide6.QtWidgets import QApplication
from src.ui.pages.disk_analyzer_page import DiskAnalyzerPage


class TestDiskAnalyzerPage(unittest.TestCase):
    """Перевіряє роботу DiskAnalyzerPage."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.page = DiskAnalyzerPage()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        worker = self.page._worker

        if worker is not None and worker.isRunning():
            worker.cancel()
            worker.wait(5000)

        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

        self.temp_dir.cleanup()

    def test_page_initializes(self) -> None:
        """Перевіряє початковий стан сторінки."""

        self.assertEqual(self.page._source_model.rowCount(), 0)
        self.assertTrue(self.page._scan_button.isEnabled())
        self.assertFalse(self.page._cancel_button.isEnabled())
        self.assertFalse(self.page._progress_bar.isVisible())

    def test_format_size(self) -> None:
        """Перевіряє форматування розміру файлів."""

        self.assertEqual(self.page._format_size(500), "500.0 B")
        self.assertEqual(self.page._format_size(1024), "1.0 KB")
        self.assertEqual(self.page._format_size(1024**2), "1.0 MB")
        self.assertEqual(self.page._format_size(1024**3), "1.0 GB")

    def test_scan_displays_files(self) -> None:
        """Перевіряє відображення результатів сканування."""

        (self.root / "first.txt").write_text("First", encoding="utf-8")
        (self.root / "second.txt").write_text("Second", encoding="utf-8")

        self.page._path_input.setText(str(self.root))
        self.page._start_scan()

        worker = self.page._worker
        self.assertIsNotNone(worker)

        self.assertTrue(worker.wait(5000))

        self.app.processEvents()

        sort_worker = self.page._sort_worker
        self.assertIsNotNone(sort_worker)

        self.assertTrue(sort_worker.wait(5000))

        self.app.processEvents()

        self.assertEqual(self.page._source_model.rowCount(), 2)
        self.assertEqual(self.page._file_count, 2)
        self.assertGreater(self.page._total_size, 0)
        self.assertTrue(self.page._scan_button.isEnabled())
        self.assertFalse(self.page._cancel_button.isEnabled())

    def test_scan_handles_missing_directory(self) -> None:
        """Перевіряє відображення помилки сканування."""

        self.page._path_input.setText(str(self.root / "missing"))
        self.page._start_scan()

        worker = self.page._worker
        self.assertIsNotNone(worker)

        self.assertTrue(worker.wait(5000))

        self.app.processEvents()

        self.assertIn("Помилка сканування", self.page._summary_label.text())
        self.assertTrue(self.page._scan_button.isEnabled())

    def test_close_cancels_active_scan(self) -> None:
        """Перевіряє завершення потоку під час закриття сторінки."""

        for index in range(100):
            (self.root / f"file_{index}.txt").write_text(
                "Test content",
                encoding="utf-8",
            )

        self.page._path_input.setText(str(self.root))
        self.page._start_scan()

        worker = self.page._worker
        self.assertIsNotNone(worker)

        self.page.close()

        self.assertFalse(worker.isRunning())
        self.assertTrue(worker._cancel_event.is_set())

    def test_scan_sorts_files_by_size_descending(self) -> None:
        """Перевіряє сортування файлів від найбільшого до найменшого."""

        (self.root / "small.txt").write_bytes(b"a" * 10)
        (self.root / "medium.txt").write_bytes(b"b" * 100)
        (self.root / "large.txt").write_bytes(b"c" * 1000)

        self.page._path_input.setText(str(self.root))
        self.page._start_scan()

        scan_worker = self.page._worker
        self.assertTrue(scan_worker.wait(5000))

        self.app.processEvents()

        sort_worker = self.page._sort_worker
        self.assertIsNotNone(sort_worker)
        self.assertTrue(sort_worker.wait(5000))

        self.app.processEvents()

        sizes = [
            self.page._source_model.entry_at(row).size
            for row in range(self.page._source_model.rowCount())
        ]

        self.assertEqual(sizes, [1000, 100, 10])


if __name__ == "__main__":
    unittest.main()
