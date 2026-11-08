"""Сервіс отримання інформації про накопичувач."""

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DiskUsage:
    """Містить показники використання накопичувача в байтах."""

    total: int
    used: int
    free: int


class DiskService:
    """Отримує інформацію про дисковий простір."""

    def get_usage(self, path: str | Path | None = None) -> DiskUsage:
        """Повертає загальний, використаний і вільний простір."""

        target_path = Path.home() if path is None else path
        usage = shutil.disk_usage(target_path)

        return DiskUsage(
            total=usage.total,
            used=usage.used,
            free=usage.free,
        )
