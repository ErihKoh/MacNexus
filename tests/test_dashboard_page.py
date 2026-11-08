"""Тести сторінки Dashboard MacNexus."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from src.ui.pages.dashboard_page import DashboardPage


class TestDashboardPage(unittest.TestCase):
    """Перевіряє сторінку огляду системи."""

    @classmethod
    def setUpClass(cls) -> None:
        """Створює екземпляр QApplication."""

        cls.app = QApplication.instance() or QApplication([])

    @patch("src.ui.pages.dashboard_page.SystemService")
    @patch("src.ui.pages.dashboard_page.MemoryService")
    @patch("src.ui.pages.dashboard_page.DiskService")
    def setUp(
        self,
        mock_disk_service,
        mock_memory_service,
        mock_system_service,
    ) -> None:
        """Створює сторінку Dashboard перед кожним тестом."""

        mock_disk_service.return_value.get_usage.return_value = SimpleNamespace(
            total=500 * 1024**3,
            used=300 * 1024**3,
            free=200 * 1024**3,
        )

        mock_memory_service.return_value.get_usage.return_value = SimpleNamespace(
            total=8 * 1024**3,
            used=5 * 1024**3,
            available=3 * 1024**3,
            percent=62.5,
        )

        mock_system_service.return_value.get_info.return_value = SimpleNamespace(
            model="MacBook Pro",
            chip="Apple M2",
            macos_version="15.0",
            architecture="arm64",
        )

        self.page = DashboardPage()

    def test_dashboard_page_creation(self) -> None:
        """Перевіряє створення сторінки."""

        self.assertIsInstance(self.page, DashboardPage)

    def test_dashboard_has_three_status_cards(self) -> None:
        """Перевіряє наявність трьох карток."""

        self.assertIsNotNone(self.page._storage_card)
        self.assertIsNotNone(self.page._memory_card)
        self.assertIsNotNone(self.page._system_card)

    def test_storage_status_displays_disk_usage(self) -> None:
        """Перевіряє відображення показників накопичувача."""

        status = self.page._storage_card._status_label.text()

        self.assertIn("Вільно 200.0 GB", status)
        self.assertIn("Використано 300.0 GB", status)
        self.assertIn("Загалом 500.0 GB", status)

    def test_storage_status_handles_error(self) -> None:
        """Перевіряє обробку помилки отримання даних накопичувача."""

        with (
            patch("src.ui.pages.dashboard_page.DiskService") as mock_disk_service,
            patch("src.ui.pages.dashboard_page.MemoryService") as mock_memory_service,
            patch("src.ui.pages.dashboard_page.SystemService") as mock_system_service,
        ):
            mock_disk_service.return_value.get_usage.side_effect = OSError

            mock_memory_service.return_value.get_usage.return_value = SimpleNamespace(
                total=8 * 1024**3,
                used=5 * 1024**3,
                available=3 * 1024**3,
                percent=62.5,
            )

            mock_system_service.return_value.get_info.return_value = SimpleNamespace(
                model="MacBook Pro",
                chip="Apple M2",
                macos_version="15.0",
                architecture="arm64",
            )

            page = DashboardPage()

        self.assertEqual(
            page._storage_card._status_label.text(),
            "Не вдалося отримати дані",
        )

    def test_memory_status_displays_memory_usage(self) -> None:
        """Перевіряє відображення показників оперативної пам'яті."""

        status = self.page._memory_card._status_label.text()

        self.assertIn("Використано 5.0 GB", status)
        self.assertIn("Доступно 3.0 GB", status)
        self.assertIn("Загалом 8.0 GB", status)

    def test_memory_status_handles_error(self) -> None:
        """Перевіряє обробку помилки отримання даних RAM."""

        with (
            patch("src.ui.pages.dashboard_page.DiskService") as mock_disk_service,
            patch("src.ui.pages.dashboard_page.SystemService") as mock_system_service,
            patch("src.ui.pages.dashboard_page.MemoryService") as mock_memory_service,
        ):
            mock_disk_service.return_value.get_usage.return_value = SimpleNamespace(
                total=500 * 1024**3,
                used=300 * 1024**3,
                free=200 * 1024**3,
            )
            mock_system_service.return_value.get_info.return_value = SimpleNamespace(
                model="MacBook Pro",
                chip="Apple M2",
                macos_version="15.0",
                architecture="arm64",
            )
            mock_memory_service.return_value.get_usage.side_effect = OSError

            page = DashboardPage()

        self.assertEqual(
            page._memory_card._status_label.text(),
            "Не вдалося отримати дані",
        )
        page.close()

    def test_system_status_handles_error(self) -> None:
        """Перевіряє обробку помилки отримання системних даних."""

        with (
            patch("src.ui.pages.dashboard_page.DiskService") as mock_disk_service,
            patch("src.ui.pages.dashboard_page.MemoryService") as mock_memory_service,
            patch("src.ui.pages.dashboard_page.SystemService") as mock_system_service,
        ):
            mock_disk_service.return_value.get_usage.return_value = SimpleNamespace(
                total=500 * 1024**3,
                used=300 * 1024**3,
                free=200 * 1024**3,
            )
            mock_memory_service.return_value.get_usage.return_value = SimpleNamespace(
                total=8 * 1024**3,
                used=5 * 1024**3,
                available=3 * 1024**3,
                percent=62.5,
            )
            mock_system_service.return_value.get_info.side_effect = OSError

            page = DashboardPage()

        self.assertEqual(
            page._system_card._status_label.text(),
            "Не вдалося отримати дані",
        )
        page.close()

    def test_dashboard_timers_are_active(self) -> None:
        """Перевіряє запуск усіх таймерів."""

        self.assertTrue(self.page._storage_timer.isActive())
        self.assertTrue(self.page._memory_timer.isActive())
        self.assertTrue(self.page._system_timer.isActive())

    def test_dashboard_timer_intervals(self) -> None:
        """Перевіряє інтервали оновлення показників."""

        self.assertEqual(
            self.page._storage_timer.interval(),
            10_000,
        )
        self.assertEqual(
            self.page._memory_timer.interval(),
            3_000,
        )
        self.assertEqual(
            self.page._system_timer.interval(),
            60_000,
        )

    def test_dashboard_timers_stop_on_close(self) -> None:
        """Перевіряє зупинку таймерів при закритті Dashboard."""

        self.page.close()

        self.assertFalse(self.page._storage_timer.isActive())
        self.assertFalse(self.page._memory_timer.isActive())
        self.assertFalse(self.page._system_timer.isActive())

    def tearDown(self) -> None:
        """Закриває Dashboard та зупиняє його таймери."""

        self.page.close()


if __name__ == "__main__":
    unittest.main()
