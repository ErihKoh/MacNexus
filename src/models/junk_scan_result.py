"""Модель результатів сканування системного сміття."""

from dataclasses import dataclass

from src.models.junk_category import JunkCategory


@dataclass(frozen=True)
class JunkScanResult:
    """Зберігає результати сканування однієї категорії."""

    category: JunkCategory
    file_count: int
    total_size: int
