"""Головна сторінка огляду системи MacNexus."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from src.services.disk_service import DiskService
from src.ui.widgets.status_card import StatusCard


class DashboardPage(QWidget):
    """Відображає загальний огляд системи."""

    def __init__(self) -> None:
        super().__init__()

        self._disk_service = DiskService()

        self._storage_card = StatusCard(
            "Сховище",
            "Завантаження...",
            show_progress=True,
        )
        self._memory_card = StatusCard("Пам'ять", "Не перевірено")
        self._system_card = StatusCard("Система", "Не перевірено")

        self._setup_ui()
        self._update_storage_status()

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

        cards_layout.addWidget(self._storage_card)
        cards_layout.addWidget(self._memory_card)
        cards_layout.addWidget(self._system_card)

        layout.addLayout(cards_layout)
        layout.addStretch()

    def _update_storage_status(self) -> None:
        """Отримує та відображає інформацію про накопичувач."""

        try:
            usage = self._disk_service.get_usage()

            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)

            usage_percent = usage.used / usage.total * 100 if usage.total > 0 else 0

            self._storage_card.set_progress(round(usage_percent))

            status = (
                f"Вільно {free_gb:.1f} GB\nВикористано {used_gb:.1f} GB\nЗагалом {total_gb:.1f} GB"
            )

        except OSError:
            status = "Не вдалося отримати дані"

        self._storage_card.set_status(status)
