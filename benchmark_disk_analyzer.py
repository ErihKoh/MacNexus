"""Benchmark повного циклу Disk Analyzer."""

import argparse
import os
import sys
import threading
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import psutil
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from src.ui.pages.disk_analyzer_page import DiskAnalyzerPage


class MemoryMonitor:
    """Вимірює RSS процесу з інтервалом 5 мс."""

    def __init__(self, interval: float = 0.005) -> None:
        self._process = psutil.Process(os.getpid())
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._monitor, daemon=True)

        self.baseline = 0
        self.peak = 0

    def start(self) -> None:
        """Запускає вимірювання."""

        self.baseline = self._process.memory_info().rss
        self.peak = self.baseline
        self._thread.start()

    def stop(self) -> None:
        """Зупиняє вимірювання."""

        self._stop_event.set()
        self._thread.join()

    def _monitor(self) -> None:
        while not self._stop_event.is_set():
            try:
                current = self._process.memory_info().rss
                self.peak = max(self.peak, current)
            except psutil.Error:
                break

            self._stop_event.wait(self._interval)


def to_mb(value: int) -> float:
    """Перетворює байти у MiB."""

    return value / (1024 * 1024)


def main() -> int:
    parser = argparse.ArgumentParser(description="Вимірювання RAM під час роботи Disk Analyzer.")
    parser.add_argument("path", type=Path, help="Каталог для сканування")
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Максимальна тривалість benchmark у секундах (за замовчуванням 1800)",
    )
    args = parser.parse_args()

    path = args.path.expanduser().resolve()

    if not path.exists() or not path.is_dir():
        print(f"Помилка: каталог не знайдено: {path}")
        return 1

    app = QApplication(sys.argv)

    page = DiskAnalyzerPage()
    page._path_input.setText(str(path))

    monitor = MemoryMonitor()
    monitor.start()

    started_at = time.perf_counter()
    timed_out = False

    def check_completion() -> None:
        nonlocal timed_out

        elapsed = time.perf_counter() - started_at

        if elapsed >= args.timeout:
            timed_out = True
            app.quit()
            return

        scan_finished = page._worker is not None and not page._worker.isRunning()

        sorting_finished = (
            page._sort_worker is not None
            and page._sort_worker.isFinished()
            and page._scan_button.isEnabled()
        )

        scan_failed = page._scan_failed and scan_finished

        if sorting_finished or scan_failed:
            app.quit()

    timer = QTimer()
    timer.timeout.connect(check_completion)
    timer.start(10)

    print(f"Каталог: {path}")
    print(f"Початкова RAM: {to_mb(monitor.baseline):.1f} MiB")
    print("Виконується сканування та сортування...")

    page._start_scan()
    app.exec()

    timer.stop()
    monitor.stop()

    elapsed = time.perf_counter() - started_at
    final_rss = psutil.Process(os.getpid()).memory_info().rss

    print("\n--- BENCHMARK RESULTS ---")
    print(f"Файлів у моделі: {page._source_model.rowCount():,}")
    print(f"Загальний розмір файлів: {to_mb(page._total_size):.1f} MiB")
    print(f"Час виконання: {elapsed:.2f} s")
    print(f"Початкова RAM: {to_mb(monitor.baseline):.1f} MiB")
    print(f"Максимальна RAM: {to_mb(monitor.peak):.1f} MiB")
    print(f"Кінцева RAM: {to_mb(final_rss):.1f} MiB")
    print(f"Приріст до піку: {to_mb(monitor.peak - monitor.baseline):.1f} MiB")

    if timed_out:
        print("ПОМИЛКА: перевищено час очікування.")
        return 1

    if page._scan_failed:
        print(f"ПОМИЛКА СКАНУВАННЯ: {page._summary_label.text()}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
