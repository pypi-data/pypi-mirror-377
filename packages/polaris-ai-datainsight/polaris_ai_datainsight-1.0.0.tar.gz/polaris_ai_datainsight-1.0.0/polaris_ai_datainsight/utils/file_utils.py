import tempfile
from pathlib import Path


def create_temp_dir(dir_path: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(dir=dir_path))
    return temp_dir
