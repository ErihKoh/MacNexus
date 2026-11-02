"""Власний перемикач світлої та темної теми."""

from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter
from PySide6.QtWidgets import QWidget


class ThemeSwitch(QWidget):
    """Компактний перемикач теми з анімованим круглим індикатором."""

    toggled = Signal(bool)

    def __init__(self, checked: bool = False) -> None:
        super().__init__()

        self._checked = checked
        self._thumb_x = 24.0 if checked else 4.0

        self.setFixedSize(48, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._animation = QVariantAnimation(self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._update_thumb_position)

    def isChecked(self) -> bool:
        """Повертає поточний стан перемикача."""

        return self._checked

    def setChecked(self, checked: bool) -> None:
        """Встановлює стан перемикача з анімацією."""

        if self._checked == checked:
            return

        self._checked = checked
        self._animate_thumb()

    def _animate_thumb(self) -> None:
        """Запускає анімацію переміщення індикатора."""

        self._animation.stop()
        self._animation.setStartValue(self._thumb_x)
        self._animation.setEndValue(24.0 if self._checked else 4.0)
        self._animation.start()

    def _update_thumb_position(self, value: float) -> None:
        """Оновлює координату індикатора під час анімації."""

        self._thumb_x = value
        self.update()

    def paintEvent(self, event) -> None:
        """Малює доріжку та круглий індикатор."""

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if self._checked:
            track_color = QColor("#b9cef0")
            thumb_color = QColor("#245db5")
        else:
            track_color = QColor("#343b49")
            thumb_color = QColor("#ffffff")

        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, 48, 28, 14, 14)

        painter.setBrush(thumb_color)
        painter.drawEllipse(
            self._thumb_x,
            4.0,
            20.0,
            20.0,
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Перемикає стан після натискання миші."""

        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self._animate_thumb()
            self.toggled.emit(self._checked)

        event.accept()
