"""Бічна панель навігації MacNexus."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from src.ui.navigation import (
    DASHBOARD_TITLE,
    SETTINGS_PAGE,
    SYSTEM_PAGES,
    TOOL_PAGES,
)


class Sidebar(QFrame):
    """Бічна панель із навігацією між сторінками."""

    page_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює структуру бічної панелі."""

        layout = QVBoxLayout(self)
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

        layout.addSpacing(12)

        system_label = QLabel("СИСТЕМА")
        system_label.setObjectName("subtitleLabel")
        layout.addWidget(system_label)

        self._add_navigation_button(layout, DASHBOARD_TITLE, 0)

        layout.addSpacing(12)

        section_label = QLabel("ІНСТРУМЕНТИ")
        section_label.setObjectName("subtitleLabel")
        layout.addWidget(section_label)

        for page_index, page_name in enumerate(TOOL_PAGES, start=1):
            self._add_navigation_button(layout, page_name, page_index)

        layout.addSpacing(12)

        system_label = QLabel("СИСТЕМА")
        system_label.setObjectName("subtitleLabel")
        layout.addWidget(system_label)

        system_start_index = 1 + len(TOOL_PAGES)

        for page_index, page_name in enumerate(
            SYSTEM_PAGES,
            start=system_start_index,
        ):
            self._add_navigation_button(layout, page_name, page_index)

        layout.addStretch()

        settings_index = 1 + len(TOOL_PAGES) + len(SYSTEM_PAGES)
        self._add_navigation_button(layout, SETTINGS_PAGE, settings_index)

        version_label = QLabel("MacNexus 0.1.0")
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)

    def _add_navigation_button(
        self,
        layout: QVBoxLayout,
        title: str,
        page_index: int,
    ) -> None:
        """Створює кнопку навігації."""

        button = QPushButton(title)
        button.setObjectName("navButton")
        button.setCheckable(True)

        self._navigation_group.addButton(button, page_index)
        layout.addWidget(button)

        button.clicked.connect(
            lambda checked=False, index=page_index: self.page_changed.emit(index)
        )

        if page_index == 0:
            button.setChecked(True)
