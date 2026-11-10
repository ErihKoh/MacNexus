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
        """Рекурсивно сканує каталог і повертає знайдені файли."""

        root = Path(path)

        if not root.exists():
            raise FileNotFoundError(f"Каталог не знайдено: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Шлях не є каталогом: {root}")

        entries = []

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
                    return entries

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

                    entries.append(entry)

                    if on_file is not None:
                        on_file(entry)

                except OSError:
                    continue

        return entries
