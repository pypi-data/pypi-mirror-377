"""Configuration management for lazycommit."""

from __future__ import annotations
import os
import re
import configparser
from pathlib import Path
from .error import KnownError

CONFIG_PATH = Path.home() / ".lazycommit"
COMMIT_TYPES = ["", "conventional"]

# Default configuration values
DEFAULTS = {
    "locale": "en",
    "generate": "1",
    "model": "openai/gpt-oss-120b",
    "timeout": "10000",
    "max-length": "50",
    "chunk-size": "4000",
    "type": "",
}


def has_own(obj: dict, key: str) -> bool:
    """Check if object has own property (like hasOwn in JS)."""
    return key in obj


def parse_assert(name: str, condition: bool, message: str) -> None:
    """Assert a condition for config parsing."""
    if not condition:
        raise KnownError(f"Invalid config property {name}: {message}")


class ConfigParsers:
    """Configuration value parsers with validation."""
    
    @staticmethod
    def GROQ_API_KEY(key: str | None) -> str:
        """Parse and validate Groq API key."""
        if not key:
            raise KnownError(
                "Please set your Groq API key via `lazycommit config set GROQ_API_KEY=<your token>`"
            )
        parse_assert("GROQ_API_KEY", key.startswith("gsk_"), 'Must start with "gsk_"')
        return key
    
    @staticmethod
    def locale(locale: str | None) -> str:
        """Parse and validate locale."""
        if not locale:
            return "en"
        
        parse_assert("locale", bool(locale), "Cannot be empty")
        parse_assert(
            "locale",
            re.match(r"^[a-z-]+$", locale, re.I) is not None,
            "Must be a valid locale (letters and dashes/underscores). You can consult the list of codes in: https://wikipedia.org/wiki/List_of_ISO_639-1_codes"
        )
        return locale
    
    @staticmethod
    def generate(count: str | None) -> int:
        """Parse and validate generate count."""
        if not count:
            return 1
        
        parse_assert("generate", count.isdigit(), "Must be an integer")
        
        parsed = int(count)
        parse_assert("generate", parsed > 0, "Must be greater than 0")
        parse_assert("generate", parsed <= 5, "Must be less or equal to 5")
        
        return parsed
    
    @staticmethod
    def type(commit_type: str | None) -> str:
        """Parse and validate commit type."""
        if not commit_type:
            return ""
        
        parse_assert(
            "type",
            commit_type in COMMIT_TYPES,
            "Invalid commit type"
        )
        
        return commit_type
    
    @staticmethod
    def proxy(url: str | None) -> str | None:
        """Parse and validate proxy URL."""
        if not url or len(url) == 0:
            return None
        
        parse_assert("proxy", url.startswith(("http://", "https://")), "Must be a valid URL")
        return url
    
    @staticmethod
    def model(model: str | None) -> str:
        """Parse and validate model."""
        if not model or len(model) == 0:
            return "openai/gpt-oss-120b"
        return model
    
    @staticmethod
    def timeout(timeout: str | None) -> int:
        """Parse and validate timeout."""
        if not timeout:
            return 10000
        
        parse_assert("timeout", timeout.isdigit(), "Must be an integer")
        
        parsed = int(timeout)
        parse_assert("timeout", parsed >= 500, "Must be greater than 500ms")
        
        return parsed
    
    @staticmethod
    def max_length(max_length: str | None) -> int:
        """Parse and validate max-length."""
        if not max_length:
            return 50
        
        parse_assert("max-length", max_length.isdigit(), "Must be an integer")
        
        parsed = int(max_length)
        parse_assert(
            "max-length",
            parsed >= 20,
            "Must be greater than 20 characters"
        )
        
        return parsed
    
    @staticmethod
    def chunk_size(chunk_size: str | None) -> int:
        """Parse and validate chunk-size."""
        if not chunk_size:
            return 4000
        
        parse_assert("chunk-size", chunk_size.isdigit(), "Must be an integer")
        
        parsed = int(chunk_size)
        parse_assert(
            "chunk-size",
            parsed >= 1000,
            "Must be at least 1000 tokens"
        )
        parse_assert(
            "chunk-size",
            parsed <= 8000,
            "Must be at most 8000 tokens (Groq limit)"
        )
        
        return parsed


# Map config keys to their parsers
CONFIG_PARSERS = {
    "GROQ_API_KEY": ConfigParsers.GROQ_API_KEY,
    "locale": ConfigParsers.locale,
    "generate": ConfigParsers.generate,
    "type": ConfigParsers.type,
    "proxy": ConfigParsers.proxy,
    "model": ConfigParsers.model,
    "timeout": ConfigParsers.timeout,
    "max-length": ConfigParsers.max_length,
    "chunk-size": ConfigParsers.chunk_size,
}


def read_config_file() -> dict[str, str]:
    """Read configuration from INI file."""
    if not CONFIG_PATH.exists():
        return {}
    
    cp = configparser.ConfigParser()
    cp.read(CONFIG_PATH)
    return dict(cp.defaults())


def load(cli_overrides: dict[str, str] | None = None, suppress: bool = False) -> dict:
    """Load and parse configuration from all sources."""
    config = read_config_file()
    parsed_config = {}
    
    for key in CONFIG_PARSERS:
        parser = CONFIG_PARSERS[key]
        value = (cli_overrides or {}).get(key) or config.get(key.lower()) or config.get(key)
        
        if suppress:
            try:
                parsed_config[key] = parser(value)
            except Exception:
                # Skip invalid config in suppress mode
                pass
        else:
            parsed_config[key] = parser(value)
    
    return parsed_config


def set_configs(key_values: list[tuple[str, str]]) -> None:
    """Set multiple configuration values."""
    config = read_config_file()
    
    for key, value in key_values:
        if not has_own(CONFIG_PARSERS, key):
            raise KnownError(f"Invalid config property: {key}")
        
        # Parse and validate the value
        parser = CONFIG_PARSERS[key]
        parsed_value = parser(value)
        
        # Store in config (convert back to string for INI file)
        if isinstance(parsed_value, bool):
            config[key.lower()] = str(parsed_value).lower()
        elif parsed_value is None:
            config.pop(key.lower(), None)  # Remove None values
        else:
            config[key.lower()] = str(parsed_value)
    
    # Write back to file
    cp = configparser.ConfigParser()
    for key, value in config.items():
        if value is not None:
            cp.set(configparser.DEFAULTSECT, key, value)
    
    with CONFIG_PATH.open("w") as f:
        cp.write(f)


# Legacy functions for backward compatibility
def set_many(pairs: list[tuple[str, str]]) -> None:
    """Set multiple config values (legacy function)."""
    set_configs(pairs)
