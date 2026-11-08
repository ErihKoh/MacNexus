"""Картка системного показника MacNexus."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StatusCard(QFrame):
    """Відображає назву та поточний стан системного показника."""

    def __init__(self, title: str, status: str) -> None:
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
        layout.addStretch()

    def set_status(self, status: str) -> None:
        """Оновлює текст поточного стану."""
        self._status_label.setText(status)
