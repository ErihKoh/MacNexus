"""Тести компонента StatusCard."""

import unittest

from PySide6.QtWidgets import QApplication, QLabel, QProgressBar
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

    def test_progress_bar_creation(self) -> None:
        """Перевіряє створення індикатора."""

        card = StatusCard("Сховище", "Перевірено", show_progress=True)
        progress = card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertEqual(progress.value(), 0)

    def test_set_progress(self) -> None:
        """Перевіряє оновлення індикатора."""

        card = StatusCard("Сховище", "Перевірено", show_progress=True)

        card.set_progress(65)

        progress = card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertEqual(progress.value(), 65)

    def test_progress_bar_turns_red_below_20_percent_free(self) -> None:
        """Перевіряє червоний колір при використанні понад 80%."""
        card = StatusCard("Сховище", "Перевірено", show_progress=True)

        card.set_progress(81)

        progress = card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertIn("#ef4444", progress.styleSheet())

    def test_progress_bar_keeps_normal_color_at_20_percent_free(self) -> None:
        """Перевіряє стандартний колір при рівно 20% вільного місця."""
        card = StatusCard("Сховище", "Перевірено", show_progress=True)

        card.set_progress(80)

        progress = card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertEqual(progress.styleSheet(), "")

    def test_progress_bar_returns_to_normal_color(self) -> None:
        """Перевіряє повернення стандартного кольору після попередження."""
        card = StatusCard("Сховище", "Перевірено", show_progress=True)

        card.set_progress(90)
        card.set_progress(70)

        progress = card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertEqual(progress.styleSheet(), "")

    def test_progress_bar_turns_red_above_80_percent(self) -> None:
        """Перевіряє червоний колір при використанні понад 80%."""

        self.card = StatusCard("Пам'ять", "Перевірено", show_progress=True)

        self.card.set_progress(80.1)

        progress = self.card.findChild(QProgressBar, "usageBar")

        self.assertIsNotNone(progress)
        self.assertIn("#ef4444", progress.styleSheet())


if __name__ == "__main__":
    unittest.main()
