"""Сервіс отримання інформації про оперативну пам'ять."""

from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class MemoryUsage:
    """Містить показники використання оперативної пам'яті в байтах."""

    total: int
    used: int
    available: int
    percent: float


class MemoryService:
    """Отримує інформацію про оперативну пам'ять."""

    def get_usage(self) -> MemoryUsage:
        """Повертає загальний, використаний і доступний обсяг RAM."""

        usage = psutil.virtual_memory()

        return MemoryUsage(
            total=usage.total,
            used=usage.total - usage.available,
            available=usage.available,
            percent=usage.percent,
        )
