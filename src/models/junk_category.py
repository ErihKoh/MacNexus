"""Модель категорії системного сміття."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JunkCategory:
    """Описує категорію потенційно зайвих файлів."""

    name: str
    description: str
    path: Path
