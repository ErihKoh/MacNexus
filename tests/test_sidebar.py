"""Тести компонента Sidebar."""

import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from src.ui.navigation import DASHBOARD_TITLE, NAVIGATION_PAGES
from src.ui.widgets.sidebar import Sidebar


class TestSidebar(unittest.TestCase):
    """Перевіряє поведінку бічної панелі."""

    @classmethod
    def setUpClass(cls) -> None:
        """Створює QApplication для тестів."""

        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        """Створює нову бічну панель перед кожним тестом."""

        self.sidebar = Sidebar()

    def test_sidebar_has_correct_number_of_navigation_buttons(self) -> None:
        """Перевіряє кількість кнопок відповідно до конфігурації."""
        buttons = self.sidebar._navigation_group.buttons()

        expected_count = len(NAVIGATION_PAGES) + 1

        self.assertEqual(len(buttons), expected_count)

    def test_dashboard_is_selected_by_default(self) -> None:
        """Перевіряє, що Огляд активний за замовчуванням."""

        self.assertEqual(
            self.sidebar._navigation_group.checkedId(),
            0,
        )

    def test_navigation_buttons_have_correct_ids(self) -> None:
        """Перевіряє індекси всіх кнопок навігації."""

        buttons = self.sidebar._navigation_group.buttons()

        buttons = self.sidebar._navigation_group.buttons()

        actual_ids = sorted(self.sidebar._navigation_group.id(button) for button in buttons)

        self.assertEqual(
            actual_ids,
            list(range(len(NAVIGATION_PAGES) + 1)),
        )

    def test_click_changes_selected_button(self) -> None:
        """Перевіряє зміну активної кнопки."""

        button = self.sidebar._navigation_group.button(2)

        QTest.mouseClick(button, Qt.MouseButton.LeftButton)

        self.assertEqual(
            self.sidebar._navigation_group.checkedId(),
            2,
        )

    def test_only_one_navigation_button_can_be_selected(self) -> None:
        """Перевіряє ексклюзивний вибір кнопок."""

        first_button = self.sidebar._navigation_group.button(0)
        second_button = self.sidebar._navigation_group.button(1)

        QTest.mouseClick(second_button, Qt.MouseButton.LeftButton)

        self.assertFalse(first_button.isChecked())
        self.assertTrue(second_button.isChecked())

    def test_page_changed_emits_correct_index(self) -> None:
        """Перевіряє передачу індексу через сигнал."""

        received_values = []
        self.sidebar.page_changed.connect(received_values.append)

        button = self.sidebar._navigation_group.button(3)

        QTest.mouseClick(button, Qt.MouseButton.LeftButton)

        self.assertEqual(received_values, [3])

    def test_navigation_buttons_match_configuration(self) -> None:
        """Перевіряє назви та індекси кнопок за конфігурацією."""
        buttons = self.sidebar._navigation_group.buttons()

        actual_pages = {
            self.sidebar._navigation_group.id(button): button.text() for button in buttons
        }

        expected_pages = {
            index: title for index, title in enumerate((DASHBOARD_TITLE, *NAVIGATION_PAGES))
        }

        self.assertEqual(actual_pages, expected_pages)


if __name__ == "__main__":
    unittest.main()
