"""Картка системного показника MacNexus."""

from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout
from src.ui.styles import CRITICAL_PROGRESS_STYLE


class StatusCard(QFrame):
    """Відображає назву та поточний стан системного показника."""

    def __init__(
        self,
        title: str,
        status: str,
        show_progress: bool = False,
    ) -> None:
        super().__init__()

        self.setObjectName("statusCard")
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("cardTitle")

        self._status_label = QLabel(status)
        self._status_label.setObjectName("cardStatus")

        layout.addWidget(self._title_label)
        layout.addWidget(self._status_label)

        self._progress_bar = None

        if show_progress:
            self._progress_bar = QProgressBar()
            self._progress_bar.setObjectName("usageBar")
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            self._progress_bar.setTextVisible(False)
            self._progress_bar.setFixedHeight(8)

            layout.addWidget(self._progress_bar)

        layout.addStretch()

    def set_status(self, status: str) -> None:
        """Оновлює текст поточного стану."""
        self._status_label.setText(status)

    def set_progress(self, value: int) -> None:
        """Оновлює індикатор та попереджає про нестачу вільного місця."""
        if self._progress_bar is not None:
            usage = max(0, min(100, value))
            self._progress_bar.setValue(usage)

            if usage > 80:
                self._progress_bar.setStyleSheet(CRITICAL_PROGRESS_STYLE)
            else:
                self._progress_bar.setStyleSheet("")
