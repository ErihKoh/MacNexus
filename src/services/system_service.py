"""Сервіс отримання інформації про систему macOS."""

import json
import platform
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemInfo:
    """Містить основні характеристики Mac."""

    model: str
    chip: str
    macos_version: str
    architecture: str


class SystemService:
    """Отримує системну інформацію засобами macOS."""

    def get_info(self) -> SystemInfo:
        """Повертає модель Mac, чип, версію macOS та архітектуру."""

        model = "Невідома модель"
        chip = "Невідомий процесор"

        try:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType", "-json"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            hardware_data = json.loads(result.stdout)
            hardware = hardware_data["SPHardwareDataType"][0]

            model = hardware.get("machine_name", model)
            chip = hardware.get("chip_type", chip)

        except (
            OSError,
            subprocess.SubprocessError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
        ):
            pass

        macos_version = platform.mac_ver()[0] or "Невідома версія"

        return SystemInfo(
            model=model,
            chip=chip,
            macos_version=macos_version,
            architecture=platform.machine(),
        )
