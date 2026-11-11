"""Сервіс визначення та сканування системного сміття."""

from collections.abc import Callable
from pathlib import Path

from src.models.junk_category import JunkCategory
from src.models.junk_scan_result import JunkScanResult
from src.services.file_scanner import FileScanner


class JunkService:
    """Визначає та сканує каталоги потенційно зайвих файлів."""

    def __init__(self) -> None:
        self._file_scanner = FileScanner()

    def get_categories(self) -> list[JunkCategory]:
        """Повертає категорії для поточного користувача macOS."""

        library = Path.home() / "Library"

        return [
            JunkCategory(
                name="User Caches",
                description="Кеші користувацьких програм",
                path=library / "Caches",
            ),
            JunkCategory(
                name="Logs",
                description="Журнали користувацьких програм",
                path=library / "Logs",
            ),
            JunkCategory(
                name="Trash",
                description="Файли у кошику користувача",
                path=Path.home() / ".Trash",
            ),
        ]

    def scan_category(
        self,
        category: JunkCategory,
        should_cancel: Callable[[], bool] | None = None,
    ) -> JunkScanResult:
        """Сканує категорію та повертає кількість і розмір файлів."""

        if not category.path.exists():
            return JunkScanResult(
                category=category,
                file_count=0,
                total_size=0,
            )

        file_count, total_size = self._file_scanner.scan_stream(
            category.path,
            should_cancel=should_cancel,
        )

        return JunkScanResult(
            category=category,
            file_count=file_count,
            total_size=total_size,
        )
