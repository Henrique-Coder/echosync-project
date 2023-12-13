from pathlib import Path
from typing import Any


def get_fullpath_string(directory: Any) -> str:
    return str(Path(directory).resolve())


def read_from_file(file_path: Path, split_by: str) -> list[str]:
    return file_path.read_text(encoding='utf-8').split(split_by)
