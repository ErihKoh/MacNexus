"""Сервіс пошуку великих файлів."""

from collections.abc import Callable
from pathlib import Path

from src.models.file_entry import FileEntry
from src.services.file_scanner import FileScanner


class LargeFileScanner:
    """Знаходить файли, розмір яких дорівнює або перевищує заданий поріг."""

    def __init__(self) -> None:
        self._scanner = FileScanner()

    def scan(
        self,
        path: str | Path,
        min_size: int,
        should_cancel: Callable[[], bool] | None = None,
    ) -> list[FileEntry]:
        """Сканує каталог і повертає великі файли за спаданням розміру."""

        if min_size < 0:
            raise ValueError("Мінімальний розмір не може бути від'ємним.")

        entries: list[FileEntry] = []

        self._scanner.scan_stream(
            path,
            should_cancel=should_cancel,
            on_file=lambda entry: entries.append(entry) if entry.size >= min_size else None,
        )

        return sorted(entries, key=lambda entry: entry.size, reverse=True)
