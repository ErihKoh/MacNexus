"""Модель інформації про знайдений файл."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileEntry:
    """Містить основні характеристики файлу."""

    path: Path
    name: str
    size: int
    modified_at: float
