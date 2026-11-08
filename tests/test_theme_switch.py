"""Тести компонента ThemeSwitch."""

import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from src.ui.widgets.theme_switch import ThemeSwitch


class TestThemeSwitch(unittest.TestCase):
    """Перевіряє поведінку перемикача теми."""

    @classmethod
    def setUpClass(cls) -> None:
        """Створює QApplication для тестів."""

        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        """Створює новий перемикач перед кожним тестом."""

        self.switch = ThemeSwitch()

    def test_initial_state_is_dark(self) -> None:
        """Перевіряє початковий темний стан."""

        self.assertFalse(self.switch.isChecked())

    def test_initial_state_can_be_light(self) -> None:
        """Перевіряє створення перемикача у світлому стані."""

        switch = ThemeSwitch(checked=True)

        self.assertTrue(switch.isChecked())

    def test_mouse_click_changes_state(self) -> None:
        """Перевіряє зміну стану після натискання."""

        QTest.mouseClick(
            self.switch,
            Qt.MouseButton.LeftButton,
        )

        self.assertTrue(self.switch.isChecked())

    def test_toggle_signal_emits_new_state(self) -> None:
        """Перевіряє передачу нового стану через сигнал."""

        received_values = []
        self.switch.toggled.connect(received_values.append)

        QTest.mouseClick(
            self.switch,
            Qt.MouseButton.LeftButton,
        )

        self.assertEqual(received_values, [True])

    def test_set_checked_changes_state(self) -> None:
        """Перевіряє програмну зміну стану."""

        self.switch.setChecked(True)

        self.assertTrue(self.switch.isChecked())

    def test_set_checked_does_not_emit_signal(self) -> None:
        """Перевіряє, що програмна зміна стану не випромінює сигнал."""

        received_values = []
        self.switch.toggled.connect(received_values.append)

        self.switch.setChecked(True)

        self.assertEqual(received_values, [])

    def test_switch_has_fixed_size(self) -> None:
        """Перевіряє розміри перемикача."""

        self.assertEqual(self.switch.width(), 48)
        self.assertEqual(self.switch.height(), 28)


if __name__ == "__main__":
    unittest.main()
