"""Сторінка аналізу системного сміття MacNexus."""

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from src.models.junk_scan_result import JunkScanResult
from src.ui.models.junk_table_model import JunkTableModel
from src.ui.workers.junk_scan_worker import JunkScanWorker


class SystemJunkPage(QWidget):
    """Відображає результати аналізу потенційно зайвих файлів."""

    def __init__(self) -> None:
        super().__init__()

        self._worker: JunkScanWorker | None = None
        self._results: list[JunkScanResult] = []
        self._scan_failed = False
        self._cancel_requested = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює інтерфейс сторінки."""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("System Junk")
        title.setObjectName("pageTitle")

        description = QLabel("Аналіз кешів, журналів і кошика. Файли не видаляються автоматично.")
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

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

        self._summary_label = QLabel("Сканування ще не виконувалося.")
        self._summary_label.setObjectName("pageDescription")

        layout.addWidget(self._summary_label)

        self._table_model = JunkTableModel()

        self._table = QTableView()
        self._table.setModel(self._table_model)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self._table, 1)

    def _start_scan(self) -> None:
        """Запускає фонове сканування категорій."""

        if self._worker is not None and self._worker.isRunning():
            return

        self._results.clear()
        self._table_model.set_results([])
        self._scan_failed = False
        self._cancel_requested = False

        self._summary_label.setText("Сканування...")
        self._progress_bar.setVisible(True)

        self._scan_button.setEnabled(False)
        self._cancel_button.setEnabled(True)

        self._worker = JunkScanWorker()
        self._worker.category_scanned.connect(self._category_scanned)
        self._worker.scan_finished.connect(self._scan_finished)
        self._worker.scan_error.connect(self._scan_error)
        self._worker.finished.connect(self._finish_worker)
        self._worker.start()

    def _category_scanned(self, result: JunkScanResult) -> None:
        """Додає результат окремої категорії."""

        self._results.append(result)
        self._table_model.set_results(self._results)
        self._update_summary()

    def _scan_finished(self, results: list[JunkScanResult]) -> None:
        """Обробляє завершення сканування."""

        self._results = results
        self._table_model.set_results(results)

        if self._cancel_requested:
            self._summary_label.setText(f"Сканування скасовано. {self._get_summary()}")
        else:
            self._summary_label.setText(f"Сканування завершено. {self._get_summary()}")

    def _scan_error(self, message: str) -> None:
        """Відображає помилку сканування."""

        self._scan_failed = True
        self._summary_label.setText(f"Помилка сканування: {message}")

    def _cancel_scan(self) -> None:
        """Надсилає запит на скасування."""

        if self._worker is not None:
            self._cancel_requested = True
            self._worker.cancel()
            self._cancel_button.setEnabled(False)
            self._summary_label.setText("Скасування сканування...")

    def _finish_worker(self) -> None:
        """Оновлює стан інтерфейсу після завершення потоку."""

        self._progress_bar.setVisible(False)
        self._scan_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._worker = None

    def _update_summary(self) -> None:
        """Оновлює загальний підсумок."""

        self._summary_label.setText(f"Знайдено: {self._get_summary()}")

    def _get_summary(self) -> str:
        """Формує загальну кількість файлів і їхній розмір."""

        file_count = sum(result.file_count for result in self._results)
        total_size = sum(result.total_size for result in self._results)

        return f"Файлів: {file_count} | Загальний розмір: {self._format_size(total_size)}"

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
        """Завершує фоновий потік перед закриттям."""

        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        super().closeEvent(event)
