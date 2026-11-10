"""Сервіс сканування файлової системи."""

from collections.abc import Callable
from pathlib import Path

from src.models.file_entry import FileEntry


class FileScanner:
    """Збирає інформацію про файли в каталозі."""

    def scan(
        self,
        path: str | Path,
        should_cancel: Callable[[], bool] | None = None,
        on_file: Callable[[FileEntry], None] | None = None,
    ) -> list[FileEntry]:
        """Сканує каталог і повертає список знайдених файлів."""

        entries: list[FileEntry] = []

        self.scan_stream(
            path,
            should_cancel=should_cancel,
            on_file=on_file or entries.append,
        )

        return entries

    def scan_stream(
        self,
        path: str | Path,
        should_cancel: Callable[[], bool] | None = None,
        on_file: Callable[[FileEntry], None] | None = None,
    ) -> tuple[int, int]:
        """Передає файли через callback без накопичення повного списку."""

        root = Path(path)

        if not root.exists():
            raise FileNotFoundError(f"Каталог не знайдено: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Шлях не є каталогом: {root}")

        file_count = 0
        total_size = 0

        def on_walk_error(_error: OSError) -> None:
            """Пропускає каталоги, до яких немає доступу."""

        for current_path, directories, filenames in root.walk(
            top_down=True,
            on_error=on_walk_error,
            follow_symlinks=False,
        ):
            if should_cancel is not None and should_cancel():
                break

            directories[:] = [
                name for name in directories if not (current_path / name).is_symlink()
            ]

            for filename in filenames:
                if should_cancel is not None and should_cancel():
                    return file_count, total_size

                file_path = current_path / filename

                try:
                    if file_path.is_symlink() or not file_path.is_file():
                        continue

                    stat = file_path.stat()

                    entry = FileEntry(
                        path=file_path,
                        name=file_path.name,
                        size=stat.st_size,
                        modified_at=stat.st_mtime,
                    )

                    file_count += 1
                    total_size += entry.size

                    if on_file is not None:
                        on_file(entry)

                except OSError:
                    continue

        return file_count, total_size
