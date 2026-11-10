"""Сторінка аналізу файлів MacNexus."""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from src.models.file_entry import FileEntry
from src.ui.widgets.sortable_table_item import SortableTableWidgetItem
from src.ui.workers.file_scan_worker import FileScanWorker


class DiskAnalyzerPage(QWidget):
    """Відображає результати сканування файлової системи."""

    def __init__(self) -> None:
        super().__init__()

        self._worker = None
        self._total_size = 0
        self._file_count = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює інтерфейс сторінки."""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("Disk Analyzer")
        title.setObjectName("pageTitle")

        description = QLabel("Аналіз файлів і використання дискового простору.")
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        path_layout = QHBoxLayout()

        self._path_input = QLineEdit(str(Path.home()))
        self._path_input.setPlaceholderText("Виберіть каталог для сканування")

        browse_button = QPushButton("Огляд")
        browse_button.clicked.connect(self._select_directory)

        path_layout.addWidget(self._path_input, 1)
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        controls_layout = QHBoxLayout()

        self._scan_button = QPushButton("Сканувати")
        self._scan_button.clicked.connect(self._start_scan)

        self._cancel_button = QPushButton("Скасувати")
        self._cancel_button.setEnabled(False)
        self._cancel_button.clicked.connect(self._cancel_scan)

        controls_layout.addWidget(self._scan_button)
        controls_layout.addWidget(self._cancel_button)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)
        self._progress_bar.setVisible(False)

        layout.addWidget(self._progress_bar)

        self._summary_label = QLabel("Файли ще не сканувалися.")
        self._summary_label.setObjectName("pageDescription")

        layout.addWidget(self._summary_label)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Назва", "Розмір", "Змінено", "Шлях"])
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self._table, 1)

    def _select_directory(self) -> None:
        """Відкриває діалог вибору каталогу."""

        directory = QFileDialog.getExistingDirectory(
            self,
            "Виберіть каталог",
            self._path_input.text(),
        )

        if directory:
            self._path_input.setText(directory)

    def _start_scan(self) -> None:
        """Запускає фонове сканування."""

        if self._worker is not None and self._worker.isRunning():
            return

        path = Path(self._path_input.text()).expanduser()

        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)

        self._total_size = 0
        self._file_count = 0

        self._summary_label.setText("Сканування...")
        self._progress_bar.setVisible(True)

        self._scan_button.setEnabled(False)
        self._cancel_button.setEnabled(True)

        self._worker = FileScanWorker(path)
        self._worker.file_found.connect(self._add_file)
        self._worker.scan_finished.connect(self._scan_finished)
        self._worker.scan_error.connect(self._scan_error)
        self._worker.finished.connect(self._finish_worker)
        self._worker.start()

    def _add_file(self, entry: FileEntry) -> None:
        """Додає знайдений файл до таблиці."""

        row = self._table.rowCount()
        self._table.insertRow(row)

        modified = datetime.fromtimestamp(entry.modified_at).strftime("%Y-%m-%d %H:%M")

        values = (
            (entry.name, entry.name.casefold()),
            (self._format_size(entry.size), entry.size),
            (modified, entry.modified_at),
            (str(entry.path), str(entry.path).casefold()),
        )

        for column, (text, sort_value) in enumerate(values):
            item = SortableTableWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, sort_value)

            if column == 1:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self._table.setItem(row, column, item)

        self._file_count += 1
        self._total_size += entry.size

        self._summary_label.setText(
            f"Знайдено файлів: {self._file_count} | "
            f"Загальний розмір: {self._format_size(self._total_size)}"
        )

    def _scan_finished(self, _results: list) -> None:
        """Обробляє завершення або скасування сканування."""

        self._summary_label.setText(
            f"Сканування завершено. Файлів: {self._file_count} | "
            f"Загальний розмір: {self._format_size(self._total_size)}"
        )

    def _scan_error(self, message: str) -> None:
        """Відображає помилку сканування."""

        self._summary_label.setText(f"Помилка сканування: {message}")

    def _cancel_scan(self) -> None:
        """Надсилає запит на скасування."""

        if self._worker is not None:
            self._worker.cancel()
            self._cancel_button.setEnabled(False)
            self._summary_label.setText("Скасування сканування...")

    def _finish_worker(self) -> None:
        """Оновлює стан елементів після завершення потоку."""

        self._progress_bar.setVisible(False)
        self._scan_button.setEnabled(True)
        self._cancel_button.setEnabled(False)

    @staticmethod
    def _format_size(size: int) -> str:
        """Перетворює байти у зручний формат."""

        value = float(size)

        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} TB"

    def closeEvent(self, event: QCloseEvent) -> None:
        """Безпечно завершує фонове сканування перед закриттям сторінки."""

        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        super().closeEvent(event)
