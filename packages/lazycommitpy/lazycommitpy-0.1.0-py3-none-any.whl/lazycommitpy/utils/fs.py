"""File system utilities."""

from pathlib import Path


async def file_exists(file_path: str | Path) -> bool:
    """Check if a file exists (async version for compatibility)."""
    return Path(file_path).exists()


def file_exists_sync(file_path: str | Path) -> bool:
    """Check if a file exists (synchronous version)."""
    return Path(file_path).exists()
