"""Тести сервісу отримання інформації про накопичувач."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services.disk_service import DiskService, DiskUsage


class TestDiskService(unittest.TestCase):
    """Перевіряє роботу DiskService."""

    def setUp(self) -> None:
        self.service = DiskService()

    @patch("src.services.disk_service.shutil.disk_usage")
    def test_get_usage_returns_disk_information(self, mock_disk_usage) -> None:
        """Перевіряє отримання показників диска."""

        mock_disk_usage.return_value = SimpleNamespace(
            total=1000,
            used=600,
            free=400,
        )

        result = self.service.get_usage("/")

        self.assertEqual(
            result,
            DiskUsage(total=1000, used=600, free=400),
        )
        mock_disk_usage.assert_called_once_with("/")

    @patch("src.services.disk_service.shutil.disk_usage")
    def test_get_usage_uses_home_directory_by_default(self, mock_disk_usage) -> None:
        """Перевіряє використання домашньої директорії за замовчуванням."""

        mock_disk_usage.return_value = SimpleNamespace(
            total=1000,
            used=600,
            free=400,
        )

        self.service.get_usage()

        mock_disk_usage.assert_called_once()

    def test_disk_usage_is_immutable(self) -> None:
        """Перевіряє незмінність показників."""

        usage = DiskUsage(total=1000, used=600, free=400)

        with self.assertRaises(AttributeError):
            usage.total = 2000


if __name__ == "__main__":
    unittest.main()
