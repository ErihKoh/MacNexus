"""Головне вікно MacNexus."""

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from src.ui.styles import THEMES
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

        sidebar = self._create_sidebar()

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

    def _create_sidebar(self) -> QFrame:
        """Створює бічну панель навігації."""

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)

        logo = QLabel("MacNexus")
        logo.setObjectName("logoLabel")

        subtitle = QLabel("SYSTEM MANAGEMENT")
        subtitle.setObjectName("subtitleLabel")

        layout.addWidget(logo)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        self._navigation_group = QButtonGroup(self)
        self._navigation_group.setExclusive(True)

        self._add_navigation_button(layout, "Огляд", 0)

        layout.addSpacing(12)

        section_label = QLabel("ІНСТРУМЕНТИ")
        section_label.setObjectName("subtitleLabel")
        layout.addWidget(section_label)

        self._add_navigation_button(layout, "System Junk", 1)
        self._add_navigation_button(layout, "Disk Analyzer", 2)
        self._add_navigation_button(layout, "Duplicates", 3)
        self._add_navigation_button(layout, "Large Files", 4)
        self._add_navigation_button(layout, "Applications", 5)
        self._add_navigation_button(layout, "Privacy", 6)
        self._add_navigation_button(layout, "Startup Manager", 7)

        layout.addSpacing(12)

        system_label = QLabel("СИСТЕМА")
        system_label.setObjectName("subtitleLabel")
        layout.addWidget(system_label)

        self._add_navigation_button(layout, "System Monitor", 8)
        self._add_navigation_button(layout, "Time Machine", 9)
        self._add_navigation_button(layout, "Maintenance", 10)

        layout.addStretch()

        self._add_navigation_button(layout, "Settings", 11)

        version_label = QLabel("MacNexus 0.1.0")
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)

        return sidebar

    def _add_navigation_button(
        self,
        layout: QVBoxLayout,
        title: str,
        page_index: int,
    ) -> None:
        """Додає кнопку навігації."""

        button = QPushButton(title)
        button.setObjectName("navButton")
        button.setCheckable(True)

        self._navigation_group.addButton(button, page_index)
        layout.addWidget(button)

        button.clicked.connect(
            lambda checked=False, index=page_index: self._pages.setCurrentIndex(index)
        )

        if page_index == 0:
            button.setChecked(True)

    def _toggle_theme(self, checked: bool) -> None:
        """Перемикає оформлення застосунку."""

        self._current_theme = "light" if checked else "dark"

        app = QApplication.instance()

        if isinstance(app, QApplication):
            app.setStyleSheet(THEMES[self._current_theme])

    def _create_pages(self) -> None:
        """Створює сторінки застосунку."""

        self._pages.addWidget(self._create_dashboard())

        page_names = [
            "System Junk",
            "Disk Analyzer",
            "Duplicates",
            "Large Files",
            "Applications",
            "Privacy",
            "Startup Manager",
            "System Monitor",
            "Time Machine",
            "Maintenance",
            "Settings",
        ]

        for page_name in page_names:
            self._pages.addWidget(self._create_placeholder_page(page_name))

    def _create_dashboard(self) -> QWidget:
        """Створює головну сторінку Dashboard."""

        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = QLabel("Огляд системи")
        header.setObjectName("pageTitle")

        description = QLabel("Стан вашого Mac та інструменти керування системою.")
        description.setObjectName("pageDescription")

        layout.addWidget(header)
        layout.addWidget(description)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        cards_layout.addWidget(self._create_status_card("Сховище", "Не перевірено"))
        cards_layout.addWidget(self._create_status_card("Пам'ять", "Не перевірено"))
        cards_layout.addWidget(self._create_status_card("Система", "Не перевірено"))

        layout.addLayout(cards_layout)
        layout.addStretch()

        return content

    def _create_placeholder_page(self, page_name: str) -> QWidget:
        """Створює тимчасову сторінку модуля."""

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel(page_name)
        title.setObjectName("pageTitle")

        description = QLabel("Цей модуль буде реалізовано на наступних етапах розробки.")
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        return page

    def _create_status_card(self, title: str, status: str) -> QFrame:
        """Створює картку системного показника."""

        card = QFrame()
        card.setObjectName("statusCard")
        card.setMinimumHeight(130)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        status_label = QLabel(status)
        status_label.setObjectName("cardStatus")

        layout.addWidget(title_label)
        layout.addWidget(status_label)
        layout.addStretch()

        return card
