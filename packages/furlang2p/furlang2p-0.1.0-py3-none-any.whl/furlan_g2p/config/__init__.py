"""Config data structures and loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schemas import NormalizerConfig, TokenizerConfig

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore[import-untyped]
except Exception:  # pragma: no cover - optional dependency
    yaml = None


def _load_mapping(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        data: dict[str, Any] = json.loads(text)
    elif p.suffix.lower() in {".yml", ".yaml"}:
        if yaml is None:
            raise ImportError("pyyaml is required for YAML config files")
        data = yaml.safe_load(text)
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported config format: {p.suffix}")
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise TypeError("Configuration file must contain a mapping")
    return data


def load_normalizer_config(path: str | Path) -> NormalizerConfig:
    """Load a :class:`NormalizerConfig` from a JSON or YAML file."""

    data = _load_mapping(path)
    return NormalizerConfig(**data)


def load_tokenizer_config(path: str | Path) -> TokenizerConfig:
    """Load a :class:`TokenizerConfig` from a JSON or YAML file."""

    data = _load_mapping(path)
    return TokenizerConfig(**data)


__all__ = [
    "load_normalizer_config",
    "load_tokenizer_config",
    "NormalizerConfig",
    "TokenizerConfig",
]
