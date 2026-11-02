"""Ініціалізація та запуск MacNexus."""

import sys

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.styles import THEMES


def run() -> int:
    """Створює та запускає застосунок."""

    app = QApplication(sys.argv)
    app.setStyleSheet(THEMES["dark"])

    window = MainWindow()
    window.show()

    return app.exec()
