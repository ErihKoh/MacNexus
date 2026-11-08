"""Тести сервісу оперативної пам'яті MacNexus."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services.memory_service import MemoryService, MemoryUsage


class TestMemoryService(unittest.TestCase):
    """Перевіряє отримання показників оперативної пам'яті."""

    @patch("src.services.memory_service.psutil.virtual_memory")
    def test_get_usage(self, mock_virtual_memory) -> None:
        """Перевіряє отримання та повернення показників RAM."""

        mock_virtual_memory.return_value = SimpleNamespace(
            total=8 * 1024**3,
            available=3 * 1024**3,
            percent=62.5,
        )

        service = MemoryService()
        usage = service.get_usage()

        self.assertIsInstance(usage, MemoryUsage)
        self.assertEqual(usage.total, 8 * 1024**3)
        self.assertEqual(usage.used, 5 * 1024**3)
        self.assertEqual(usage.available, 3 * 1024**3)
        self.assertEqual(usage.percent, 62.5)

        mock_virtual_memory.assert_called_once()


if __name__ == "__main__":
    unittest.main()
