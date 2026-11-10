"""Тести моделі FileEntry."""

import unittest
from pathlib import Path

from src.models.file_entry import FileEntry


class TestFileEntry(unittest.TestCase):
    """Перевіряє модель інформації про файл."""

    def test_file_entry_stores_file_information(self) -> None:
        """Перевіряє збереження характеристик файлу."""

        entry = FileEntry(
            path=Path("/Users/test/document.pdf"),
            name="document.pdf",
            size=1024,
            modified_at=1700000000.0,
        )

        self.assertEqual(entry.path, Path("/Users/test/document.pdf"))
        self.assertEqual(entry.name, "document.pdf")
        self.assertEqual(entry.size, 1024)
        self.assertEqual(entry.modified_at, 1700000000.0)

    def test_file_entry_is_immutable(self) -> None:
        """Перевіряє незмінність моделі."""

        entry = FileEntry(
            path=Path("/Users/test/document.pdf"),
            name="document.pdf",
            size=1024,
            modified_at=1700000000.0,
        )

        with self.assertRaises(AttributeError):
            entry.size = 2048


if __name__ == "__main__":
    unittest.main()
