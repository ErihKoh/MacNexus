"""Головне вікно MacNexus."""

from PySide6.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    """Головне вікно застосунку."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("MacNexus")
        self.resize(1200, 800)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Ініціалізує структуру головного вікна."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
