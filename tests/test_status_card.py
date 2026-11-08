"""Тести компонента StatusCard."""

import unittest

from PySide6.QtWidgets import QApplication, QLabel
from src.ui.widgets.status_card import StatusCard


class TestStatusCard(unittest.TestCase):
    """Перевіряє створення та роботу картки системного показника."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.card = StatusCard("Сховище", "Не перевірено")

    def test_object_name(self) -> None:
        self.assertEqual(self.card.objectName(), "statusCard")

    def test_minimum_height(self) -> None:
        self.assertEqual(self.card.minimumHeight(), 130)

    def test_title_label(self) -> None:
        label = self.card.findChild(QLabel, "cardTitle")

        self.assertIsNotNone(label)
        self.assertEqual(label.text(), "Сховище")

    def test_status_label(self) -> None:
        label = self.card.findChild(QLabel, "cardStatus")

        self.assertIsNotNone(label)
        self.assertEqual(label.text(), "Не перевірено")

    def test_set_status(self) -> None:
        self.card.set_status("Перевірено")

        label = self.card.findChild(QLabel, "cardStatus")

        self.assertIsNotNone(label)
        self.assertEqual(label.text(), "Перевірено")


if __name__ == "__main__":
    unittest.main()
