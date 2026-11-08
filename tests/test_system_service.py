"""Тести сервісу системної інформації."""

import json
import unittest
from unittest.mock import patch

from src.services.system_service import SystemService


class TestSystemService(unittest.TestCase):
    """Перевіряє отримання інформації про Mac."""

    @patch("src.services.system_service.platform.machine")
    @patch("src.services.system_service.platform.mac_ver")
    @patch("src.services.system_service.subprocess.run")
    def test_get_info(
        self,
        mock_run,
        mock_mac_ver,
        mock_machine,
    ) -> None:
        """Перевіряє отримання характеристик системи."""

        mock_run.return_value.stdout = json.dumps(
            {
                "SPHardwareDataType": [
                    {
                        "machine_name": "MacBook Pro",
                        "chip_type": "Apple M2",
                    }
                ]
            }
        )

        mock_mac_ver.return_value = ("15.0", ("", "", ""), "")
        mock_machine.return_value = "arm64"

        info = SystemService().get_info()

        self.assertEqual(info.model, "MacBook Pro")
        self.assertEqual(info.chip, "Apple M2")
        self.assertEqual(info.macos_version, "15.0")
        self.assertEqual(info.architecture, "arm64")

        mock_run.assert_called_once()

    @patch("src.services.system_service.platform.machine")
    @patch("src.services.system_service.platform.mac_ver")
    @patch("src.services.system_service.subprocess.run")
    def test_get_info_handles_command_error(
        self,
        mock_run,
        mock_mac_ver,
        mock_machine,
    ) -> None:
        """Перевіряє резервні значення при помилці системної команди."""

        mock_run.side_effect = OSError
        mock_mac_ver.return_value = ("15.0", ("", "", ""), "")
        mock_machine.return_value = "arm64"

        info = SystemService().get_info()

        self.assertEqual(info.model, "Невідома модель")
        self.assertEqual(info.chip, "Невідомий процесор")
        self.assertEqual(info.macos_version, "15.0")
        self.assertEqual(info.architecture, "arm64")


if __name__ == "__main__":
    unittest.main()
