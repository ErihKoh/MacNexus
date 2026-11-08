"""Головна сторінка огляду системи MacNexus."""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from src.services.disk_service import DiskService
from src.services.memory_service import MemoryService
from src.services.system_service import SystemService
from src.ui.widgets.status_card import StatusCard


class DashboardPage(QWidget):
    """Відображає загальний огляд системи."""

    STORAGE_REFRESH_INTERVAL = 10_000
    MEMORY_REFRESH_INTERVAL = 3_000
    SYSTEM_REFRESH_INTERVAL = 60_000

    def __init__(self) -> None:
        super().__init__()

        self._disk_service = DiskService()
        self._memory_service = MemoryService()
        self._system_service = SystemService()
        self._setup_timers()

        self._storage_card = StatusCard(
            "Сховище",
            "Завантаження...",
            show_progress=True,
        )
        self._memory_card = StatusCard(
            "Пам'ять",
            "Завантаження...",
            show_progress=True,
        )
        self._system_card = StatusCard("Система", "Не перевірено")

        self._setup_ui()
        self._update_storage_status()
        self._update_memory_status()
        self._update_system_status()

    def _setup_timers(self) -> None:
        """Створює та запускає таймери оновлення системних показників."""

        self._storage_timer = QTimer(self)
        self._storage_timer.setInterval(self.STORAGE_REFRESH_INTERVAL)
        self._storage_timer.timeout.connect(self._update_storage_status)

        self._memory_timer = QTimer(self)
        self._memory_timer.setInterval(self.MEMORY_REFRESH_INTERVAL)
        self._memory_timer.timeout.connect(self._update_memory_status)

        self._system_timer = QTimer(self)
        self._system_timer.setInterval(self.SYSTEM_REFRESH_INTERVAL)
        self._system_timer.timeout.connect(self._update_system_status)

        self._storage_timer.start()
        self._memory_timer.start()
        self._system_timer.start()

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

    def _update_memory_status(self) -> None:
        """Отримує та відображає інформацію про оперативну пам'ять."""

        try:
            usage = self._memory_service.get_usage()

            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            available_gb = usage.available / (1024**3)

            self._memory_card.set_progress(usage.percent)

            status = (
                f"Використано {used_gb:.1f} GB\n"
                f"Доступно {available_gb:.1f} GB\n"
                f"Загалом {total_gb:.1f} GB"
            )

        except OSError:
            status = "Не вдалося отримати дані"

        self._memory_card.set_status(status)

    def _update_system_status(self) -> None:
        """Отримує та відображає інформацію про систему."""

        try:
            info = self._system_service.get_info()

            status = (
                f"Модель: {info.model}\n"
                f"Чип: {info.chip}\n"
                f"macOS: {info.macos_version}\n"
                f"Архітектура: {info.architecture}"
            )

        except OSError:
            status = "Не вдалося отримати дані"

        self._system_card.set_status(status)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Зупиняє таймери перед закриттям Dashboard."""

        self._storage_timer.stop()
        self._memory_timer.stop()
        self._system_timer.stop()

        super().closeEvent(event)
