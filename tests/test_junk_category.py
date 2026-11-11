"""Тести моделі категорії системного сміття."""

import unittest
from pathlib import Path

from src.models.junk_category import JunkCategory


class TestJunkCategory(unittest.TestCase):
    """Перевіряє модель JunkCategory."""

    def test_category_stores_values(self) -> None:
        """Перевіряє збереження параметрів категорії."""

        category = JunkCategory(
            name="User Caches",
            description="Кеші користувача",
            path=Path.home() / "Library" / "Caches",
        )

        self.assertEqual(category.name, "User Caches")
        self.assertEqual(category.description, "Кеші користувача")
        self.assertEqual(
            category.path,
            Path.home() / "Library" / "Caches",
        )

    def test_category_is_immutable(self) -> None:
        """Перевіряє незмінність моделі."""

        category = JunkCategory(
            name="Logs",
            description="Журнали",
            path=Path.home() / "Library" / "Logs",
        )

        with self.assertRaises(AttributeError):
            category.name = "Other"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
