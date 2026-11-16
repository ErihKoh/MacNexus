"""Вкладка пошуку великих файлів MacNexus."""

from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from src.ui.models.file_table_model import FileTableModel
from src.ui.workers.large_file_scan_worker import LargeFileScanWorker


class LargeFilesTab(QWidget):
    """Інтерфейс пошуку великих файлів."""

    def __init__(self) -> None:
        super().__init__()

        self._selected_path: Path | None = None
        self._table_model = FileTableModel()

        self._worker: LargeFileScanWorker | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Створює елементи інтерфейсу."""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        path_layout = QHBoxLayout()

        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText("Виберіть каталог для сканування")
        self._path_input.setReadOnly(True)

        self._browse_button = QPushButton("Вибрати каталог")
        self._browse_button.clicked.connect(self._select_directory)

        path_layout.addWidget(self._path_input, 1)
        path_layout.addWidget(self._browse_button)

        layout.addLayout(path_layout)

        size_layout = QHBoxLayout()

        size_label = QLabel("Мінімальний розмір:")
        self._min_size_input = QSpinBox()
        self._min_size_input.setRange(1, 1_048_576)
        self._min_size_input.setValue(100)
        self._min_size_input.setSuffix(" MB")

        size_layout.addWidget(size_label)
        size_layout.addWidget(self._min_size_input)
        size_layout.addStretch()

        layout.addLayout(size_layout)

        controls_layout = QHBoxLayout()

        self._scan_button = QPushButton("Знайти великі файли")
        self._scan_button.clicked.connect(self._start_scan)
        self._scan_button.setEnabled(False)

        self._cancel_button = QPushButton("Скасувати")
        self._cancel_button.clicked.connect(self._cancel_scan)
        self._cancel_button.setEnabled(False)

        controls_layout.addWidget(self._scan_button)
        controls_layout.addWidget(self._cancel_button)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)
        self._progress_bar.setVisible(False)

        layout.addWidget(self._progress_bar)

        self._summary_label = QLabel("Виберіть каталог для початку пошуку.")
        self._summary_label.setObjectName("pageDescription")

        layout.addWidget(self._summary_label)

        self._table = QTableView()
        self._table.setModel(self._table_model)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self._table, 1)

    def _select_directory(self) -> None:
        """Відкриває діалог вибору каталогу."""

        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Виберіть каталог для сканування",
        )

        if not selected_path:
            return

        self._selected_path = Path(selected_path)
        self._path_input.setText(str(self._selected_path))
        self._scan_button.setEnabled(True)
        self._summary_label.setText("Каталог вибрано. Можна починати пошук.")

    def _get_min_size_bytes(self) -> int:
        """Повертає мінімальний розмір у байтах."""

        return self._min_size_input.value() * 1024 * 1024

    def _start_scan(self) -> None:
        """Запускає пошук великих файлів у фоновому потоці."""

        if self._worker is not None and self._worker.isRunning():
            return

        if self._selected_path is None:
            return

        self._table_model.clear()
        self._summary_label.setText("Пошук великих файлів...")
        self._progress_bar.setVisible(True)

        self._browse_button.setEnabled(False)
        self._min_size_input.setEnabled(False)
        self._scan_button.setEnabled(False)
        self._cancel_button.setEnabled(True)

        self._worker = LargeFileScanWorker(
            self._selected_path,
            min_size=self._get_min_size_bytes(),
        )

        self._worker.scan_finished.connect(self._scan_finished)
        self._worker.scan_error.connect(self._scan_error)
        self._worker.finished.connect(self._finish_worker)

        self._worker.start()

    def _scan_finished(self, entries: list, cancelled: bool) -> None:
        """Відображає результати пошуку."""

        self._table_model.replace_entries(entries)

        total_size = sum(entry.size for entry in entries)
        summary = f"Файлів: {len(entries)} | Загальний розмір: {self._format_size(total_size)}"

        if cancelled:
            self._summary_label.setText(f"Пошук скасовано. {summary}")
        else:
            self._summary_label.setText(f"Пошук завершено. {summary}")

    def _scan_error(self, message: str) -> None:
        """Відображає помилку пошуку."""

        self._summary_label.setText(f"Помилка сканування: {message}")

    def _cancel_scan(self) -> None:
        """Надсилає запит на скасування пошуку."""

        if self._worker is not None:
            self._worker.cancel()
            self._cancel_button.setEnabled(False)
            self._summary_label.setText("Скасування пошуку...")

    def _finish_worker(self) -> None:
        """Відновлює інтерфейс після завершення потоку."""

        self._progress_bar.setVisible(False)

        self._browse_button.setEnabled(True)
        self._min_size_input.setEnabled(True)
        self._scan_button.setEnabled(self._selected_path is not None)
        self._cancel_button.setEnabled(False)

        self._worker = None

    @staticmethod
    def _format_size(size: int) -> str:
        """Форматує розмір у зручні одиниці."""

        value = float(size)

        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} TB"

    def stop_scan(self) -> None:
        """Зупиняє фонове сканування та очікує завершення потоку."""

        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Завершує фоновий потік перед закриттям вкладки."""

        self.stop_scan()
        super().closeEvent(event)
