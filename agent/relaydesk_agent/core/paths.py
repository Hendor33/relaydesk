from pathlib import Path

def validated_path(value: str, *, must_exist: bool = True, directory: bool | None = None) -> Path:
    if not value or "\x00" in value:
        raise ValueError("Path is empty or invalid.")
    raw = Path(value).expanduser()
    if ".." in raw.parts:
        raise ValueError("Path traversal is not allowed.")
    if not raw.is_absolute():
        raise ValueError("Path must be absolute.")
    path = raw.resolve(strict=False)
    if must_exist and not path.exists():
        raise ValueError("Configured path does not exist.")
    if directory is True and path.exists() and not path.is_dir():
        raise ValueError("Destination directory does not exist.")
    if directory is False and path.exists() and not path.is_file():
        raise ValueError("Expected a file path.")
    return path

def destination_for(directory: str, source: Path, name: str | None = None) -> Path:
    parent = validated_path(directory, directory=True)
    candidate = (parent / (name or source.name)).resolve(strict=False)
    if candidate.parent != parent:
        raise ValueError("Destination escapes the configured directory.")
    if candidate.exists():
        raise FileExistsError(f"Destination already exists: {candidate}")
    return candidate
