"""Сторінка-заглушка MacNexus."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    """Відображає сторінку, функціональність якої ще не реалізована."""

    def __init__(self, title: str) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        description_label = QLabel("Цей розділ буде доступний у наступних версіях MacNexus.")
        description_label.setObjectName("pageDescription")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
