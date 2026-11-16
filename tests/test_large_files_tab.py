"""Тести вкладки пошуку великих файлів."""

import tempfile
import time
import unittest
from pathlib import Path

from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication
from src.ui.pages.large_files_tab import LargeFilesTab


class TestLargeFilesTab(unittest.TestCase):
    """Перевіряє роботу LargeFilesTab."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.tab = LargeFilesTab()

    def tearDown(self) -> None:
        worker = self.tab._worker

        if worker is not None and worker.isRunning():
            worker.cancel()
            worker.wait(5000)

        self.tab.close()
        self.tab.deleteLater()
        self.app.processEvents()
        self.temp_dir.cleanup()

    def _run_worker(self) -> None:
        """Очікує завершення фонового потоку."""

        worker = self.tab._worker
        self.assertIsNotNone(worker)

        finished_spy = QSignalSpy(worker.finished)

        deadline = time.monotonic() + 5

        while finished_spy.count() == 0 and time.monotonic() < deadline:
            finished_spy.wait(100)

        if not worker.wait(1000):
            worker.cancel()
            worker.wait(5000)

        self.app.processEvents()

        self.assertEqual(finished_spy.count(), 1)
        self.assertFalse(worker.isRunning())

    def test_tab_initializes(self) -> None:
        """Перевіряє початковий стан інтерфейсу."""

        self.assertEqual(self.tab._table_model.rowCount(), 0)
        self.assertEqual(self.tab._min_size_input.value(), 100)

        self.assertFalse(self.tab._scan_button.isEnabled())
        self.assertFalse(self.tab._cancel_button.isEnabled())
        self.assertFalse(self.tab._progress_bar.isVisible())

    def test_get_min_size_bytes(self) -> None:
        """Перевіряє перетворення мегабайтів у байти."""

        self.tab._min_size_input.setValue(250)

        self.assertEqual(
            self.tab._get_min_size_bytes(),
            250 * 1024 * 1024,
        )

    def test_select_directory(self) -> None:
        """Перевіряє встановлення вибраного каталогу."""

        self.tab._selected_path = self.root
        self.tab._path_input.setText(str(self.root))
        self.tab._scan_button.setEnabled(True)

        self.assertEqual(self.tab._selected_path, self.root)
        self.assertEqual(self.tab._path_input.text(), str(self.root))
        self.assertTrue(self.tab._scan_button.isEnabled())

    def test_scan_displays_large_files(self) -> None:
        """Перевіряє пошук і відображення великих файлів."""

        large_file = self.root / "large.bin"
        large_file.write_bytes(b"a" * (2 * 1024 * 1024))

        self.tab._selected_path = self.root
        self.tab._min_size_input.setValue(1)
        self.tab._start_scan()

        self._run_worker()

        self.assertEqual(self.tab._table_model.rowCount(), 1)
        self.assertEqual(
            self.tab._table_model.entry_at(0).name,
            "large.bin",
        )
        self.assertIn("Файлів: 1", self.tab._summary_label.text())
        self.assertIn("Пошук завершено", self.tab._summary_label.text())
        self.assertTrue(self.tab._scan_button.isEnabled())
        self.assertFalse(self.tab._cancel_button.isEnabled())

    def test_scan_error(self) -> None:
        """Перевіряє відображення помилки."""

        self.tab._scan_error("Тестова помилка")

        self.assertEqual(
            self.tab._summary_label.text(),
            "Помилка сканування: Тестова помилка",
        )

    def test_cancel_scan(self) -> None:
        """Перевіряє надсилання запиту скасування."""

        self.tab._selected_path = self.root
        self.tab._start_scan()

        worker = self.tab._worker
        self.assertIsNotNone(worker)

        self.tab._cancel_scan()

        self.assertTrue(worker._cancel_event.is_set())
        self.assertFalse(self.tab._cancel_button.isEnabled())

        self._run_worker()

    def test_format_size(self) -> None:
        """Перевіряє форматування розміру."""

        self.assertEqual(self.tab._format_size(500), "500.0 B")
        self.assertEqual(self.tab._format_size(1024), "1.0 KB")
        self.assertEqual(self.tab._format_size(1024**2), "1.0 MB")


if __name__ == "__main__":
    unittest.main()
