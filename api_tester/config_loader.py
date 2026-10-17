
"""Load and validate API testing configuration profiles."""

from pathlib import Path
from urllib.parse import urlparse

import yaml


def load_config(config_path: str) -> dict:
    """Load a YAML configuration file and validate its structure."""
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML configuration: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML mapping.")

    target = config.get("target")
    if not isinstance(target, dict):
        raise ValueError("Missing or invalid 'target' section.")

    base_url = target.get("base_url")
    if not isinstance(base_url, str):
        raise ValueError("'target.base_url' must be a URL string.")

    parsed_url = urlparse(base_url)

    if (
        parsed_url.scheme not in {"http", "https"}
        or not parsed_url.hostname
        or parsed_url.username
        or parsed_url.password
    ):
        raise ValueError(
            "'target.base_url' must be a valid HTTP(S) URL "
            "without embedded credentials."
        )

    checks = config.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError("'checks' must be a list.")

    if not all(isinstance(check, str) for check in checks):
        raise ValueError("Each check name must be a string.")

    return config
