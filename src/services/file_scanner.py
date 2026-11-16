"""Сервіс сканування файлової системи."""

from collections.abc import Callable
from pathlib import Path

from src.models.directory_entry import DirectoryEntry
from src.models.file_entry import FileEntry


class FileScanner:
    """Збирає інформацію про файли та директорії."""

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
        on_directory: Callable[[DirectoryEntry], None] | None = None,
    ) -> tuple[int, int]:
        """Передає файли під час обходу та статистику директорій після нього."""

        root = Path(path)

        if not root.exists():
            raise FileNotFoundError(f"Каталог не знайдено: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Шлях не є каталогом: {root}")

        file_count = 0
        total_size = 0

        directory_stats: dict[Path, list[int]] = {}
        visited_directories: list[Path] = []

        def on_walk_error(_error: OSError) -> None:
            """Пропускає каталоги, до яких немає доступу."""

        cancelled = False

        for current_path, directories, filenames in root.walk(
            top_down=True,
            on_error=on_walk_error,
            follow_symlinks=False,
        ):
            if should_cancel is not None and should_cancel():
                cancelled = True
                break

            visited_directories.append(current_path)
            directory_stats[current_path] = [0, 0]

            directories[:] = [
                name for name in directories if not (current_path / name).is_symlink()
            ]

            for directory in directories:
                directory_stats[current_path / directory] = [0, 0]

            for filename in filenames:
                if should_cancel is not None and should_cancel():
                    cancelled = True
                    break

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

                    directory_stats[current_path][0] += entry.size
                    directory_stats[current_path][1] += 1

                    if on_file is not None:
                        on_file(entry)

                except OSError:
                    continue

            if cancelled:
                break

        for directory in reversed(visited_directories):
            if directory == root:
                continue

            parent = directory.parent

            if parent in directory_stats:
                directory_stats[parent][0] += directory_stats[directory][0]
                directory_stats[parent][1] += directory_stats[directory][1]

        if on_directory is not None:
            for directory in visited_directories:
                size, count = directory_stats[directory]

                on_directory(
                    DirectoryEntry(
                        path=directory,
                        name=directory.name or str(directory),
                        size=size,
                        file_count=count,
                    )
                )

        return file_count, total_size
