"""Головна сторінка огляду системи MacNexus."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from src.ui.widgets.status_card import StatusCard


class DashboardPage(QWidget):
    """Відображає загальний огляд системи."""

    def __init__(self) -> None:
        super().__init__()

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює та компонувує елементи Dashboard."""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("Огляд системи")
        title.setObjectName("pageTitle")

        description = QLabel("Загальний стан вашого Mac та основні системні показники.")
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        cards_layout.addWidget(StatusCard("Сховище", "Не перевірено"))
        cards_layout.addWidget(StatusCard("Пам'ять", "Не перевірено"))
        cards_layout.addWidget(StatusCard("Система", "Не перевірено"))

        layout.addLayout(cards_layout)
        layout.addStretch()
