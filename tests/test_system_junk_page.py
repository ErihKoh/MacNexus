"""Тести сторінки System Junk."""

import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy
from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult
from src.ui.pages.system_junk_page import SystemJunkPage


class FakeJunkService:
    """Тестовий сервіс сканування."""

    def get_categories(self) -> list[JunkCategory]:
        return [
            JunkCategory("Caches", "Кеші", Path("/test/caches")),
            JunkCategory("Logs", "Журнали", Path("/test/logs")),
        ]

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


class TestSystemJunkPage(unittest.TestCase):
    """Перевіряє роботу SystemJunkPage."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance()

        if cls.app is None:
            from PySide6.QtWidgets import QApplication

            cls.app = QApplication([])

    def setUp(self) -> None:
        self.page = SystemJunkPage()

    def tearDown(self) -> None:
        worker = self.page._worker

        if worker is not None and worker.isRunning():
            worker.cancel()
            worker.wait(5000)

        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

    def test_page_initializes(self) -> None:
        """Перевіряє початковий стан сторінки."""

        self.assertEqual(self.page._table_model.rowCount(), 0)
        self.assertTrue(self.page._scan_button.isEnabled())
        self.assertFalse(self.page._cancel_button.isEnabled())
        self.assertFalse(self.page._progress_bar.isVisible())

    def test_format_size(self) -> None:
        """Перевіряє форматування розміру."""

        self.assertEqual(self.page._format_size(500), "500.0 B")
        self.assertEqual(self.page._format_size(1024), "1.0 KB")
        self.assertEqual(self.page._format_size(1024**2), "1.0 MB")
        self.assertEqual(self.page._format_size(1024**3), "1.0 GB")

    def test_get_summary(self) -> None:
        """Перевіряє формування загального підсумку."""

        category = JunkCategory("Caches", "Кеші", Path("/test/caches"))

        self.page._results = [
            JunkScanResult(category, 2, 1024),
            JunkScanResult(category, 3, 2048),
        ]

        self.assertEqual(
            self.page._get_summary(),
            "Файлів: 5 | Загальний розмір: 3.0 KB",
        )

    def test_scan_displays_categories(self) -> None:
        """Перевіряє відображення результатів сканування."""

        self.page._start_scan()

        worker = self.page._worker
        self.assertIsNotNone(worker)

        worker._service = FakeJunkService()

        finished_spy = QSignalSpy(worker.finished)

        deadline = 5

        while finished_spy.count() == 0 and deadline > 0:
            self.app.processEvents()
            finished_spy.wait(100)
            deadline -= 1

        self.assertTrue(worker.wait(5000))
        self.app.processEvents()

        self.assertEqual(self.page._table_model.rowCount(), 2)
        self.assertEqual(len(self.page._results), 2)
        self.assertTrue(self.page._scan_button.isEnabled())
        self.assertFalse(self.page._cancel_button.isEnabled())

        self.assertIn("Файлів: 4", self.page._summary_label.text())
        self.assertIn("2.0 KB", self.page._summary_label.text())

    def test_cancel_scan(self) -> None:
        """Перевіряє надсилання запиту на скасування."""

        self.page._start_scan()

        worker = self.page._worker
        self.assertIsNotNone(worker)

        self.page._cancel_scan()

        self.assertTrue(worker._cancel_event.is_set())
        self.assertFalse(self.page._cancel_button.isEnabled())


if __name__ == "__main__":
    unittest.main()
