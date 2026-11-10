"""Сторінка аналізу файлів MacNexus."""

from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from src.models.file_entry import FileEntry
from src.ui.models.file_sort_proxy_model import FileSortProxyModel
from src.ui.models.file_table_model import FileTableModel
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

        self._source_model = FileTableModel()

        self._proxy_model = FileSortProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)

        self._table = QTableView()
        self._table.setModel(self._proxy_model)
        self._table.setSortingEnabled(True)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
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
        self._proxy_model.setDynamicSortFilter(False)
        self._source_model.clear()

        self._total_size = 0
        self._file_count = 0

        self._summary_label.setText("Сканування...")
        self._progress_bar.setVisible(True)

        self._scan_button.setEnabled(False)
        self._cancel_button.setEnabled(True)

        self._worker = FileScanWorker(path)
        self._worker.batch_found.connect(self._add_batch)
        self._worker.scan_finished.connect(self._scan_finished)
        self._worker.scan_error.connect(self._scan_error)
        self._worker.finished.connect(self._finish_worker)
        self._worker.start()

    def _add_batch(self, entries: list[FileEntry]) -> None:
        """Додає пакет файлів до моделі."""

        if not entries:
            return

        self._source_model.append_entries(entries)

        self._file_count += len(entries)
        self._total_size += sum(entry.size for entry in entries)

        self._update_summary()

    def _scan_finished(self, file_count: int, total_size: int) -> None:
        """Обробляє завершення сканування."""

        self._file_count = file_count
        self._total_size = total_size

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

        self._proxy_model.setDynamicSortFilter(True)

        header = self._table.horizontalHeader()
        self._proxy_model.sort(
            header.sortIndicatorSection(),
            header.sortIndicatorOrder(),
        )

        self._table.setSortingEnabled(True)

        self._progress_bar.setVisible(False)
        self._scan_button.setEnabled(True)
        self._cancel_button.setEnabled(False)

    def _update_summary(self) -> None:
        """Оновлює підсумок сканування."""

        self._summary_label.setText(
            f"Знайдено файлів: {self._file_count} | "
            f"Загальний розмір: {self._format_size(self._total_size)}"
        )

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
        """Безпечно завершує фонове сканування перед закриттям."""

        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        super().closeEvent(event)
