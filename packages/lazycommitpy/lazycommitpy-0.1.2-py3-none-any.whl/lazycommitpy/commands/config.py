"""Configuration command implementation."""

from ..utils.config import load, set_configs, has_own
from ..utils.error import KnownError


def get_config(keys: list[str]) -> None:
    """Get configuration values."""
    cfg = load(suppress=True)
    for key in keys:
        if has_own(cfg, key):
            print(f"{key}={cfg[key]}")


def set_config(pairs: list[tuple[str, str]]) -> None:
    """Set configuration values."""
    set_configs(pairs)
