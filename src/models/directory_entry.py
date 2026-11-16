"""Модель інформації про каталог."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DirectoryEntry:
    """Містить сумарну статистику каталогу."""

    path: Path
    name: str
    size: int
    file_count: int
