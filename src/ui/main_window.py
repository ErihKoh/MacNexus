"""Головне вікно MacNexus."""

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from src.ui.navigation import NAVIGATION_PAGES
from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.disk_analyzer_page import DiskAnalyzerPage
from src.ui.pages.placeholder_page import PlaceholderPage
from src.ui.styles import THEMES
from src.ui.widgets.sidebar import Sidebar
from src.ui.widgets.theme_switch import ThemeSwitch


class MainWindow(QMainWindow):
    """Головне вікно застосунку."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("MacNexus")
        self.resize(1200, 800)

        self._current_theme = "dark"

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює основну структуру інтерфейсу."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._pages = QStackedWidget()

        sidebar = Sidebar()
        sidebar.page_changed.connect(self._pages.setCurrentIndex)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(24, 12, 24, 0)

        top_bar.addStretch()

        self._theme_switch = ThemeSwitch()
        self._theme_switch.toggled.connect(self._toggle_theme)

        top_bar.addWidget(self._theme_switch)

        content_layout.addLayout(top_bar)
        content_layout.addWidget(self._pages, 1)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        self._create_pages()

    def _toggle_theme(self, checked: bool) -> None:
        """Перемикає оформлення застосунку."""

        self._current_theme = "light" if checked else "dark"

        app = QApplication.instance()

        if isinstance(app, QApplication):
            app.setStyleSheet(THEMES[self._current_theme])

    def _create_pages(self) -> None:
        """Створює сторінки застосунку."""

        self._pages.addWidget(DashboardPage())

        for page_name in NAVIGATION_PAGES:
            page = self._create_page(page_name)
            self._pages.addWidget(page)

    def _create_page(self, page_name: str) -> QWidget:
        """Створює відповідну сторінку за назвою."""

        if page_name == "Disk Analyzer":
            return DiskAnalyzerPage()

        return PlaceholderPage(page_name)
