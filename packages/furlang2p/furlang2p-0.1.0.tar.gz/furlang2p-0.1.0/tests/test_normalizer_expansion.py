"""Tests for Normalizer expansion and config loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from furlan_g2p.config import NormalizerConfig, load_normalizer_config
from furlan_g2p.normalization.normalizer import Normalizer


def test_basic_expansions() -> None:
    cfg = NormalizerConfig(
        numbers_map={"2": "doi"},
        units_map={"kg": "chilogram"},
        abbreviations_map={"sig": "siôr"},
        acronyms_map={"sos": "esse o esse"},
    )
    norm = Normalizer(cfg)
    assert norm.normalize("2 kg, Sig. SOS") == "doi chilogram _ siôr __ esse o esse"


def test_number_spellout() -> None:
    norm = Normalizer()
    assert norm.normalize("2004") == "doi mil e cuatri"
    assert norm.normalize("1964") == "mil nûfcent e sessantecuatri"


def test_load_config_json(tmp_path: Path) -> None:
    data = {
        "numbers_map": {"3": "trê"},
        "abbreviations_map": {"pt": "part"},
    }
    path = tmp_path / "norm.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    cfg = load_normalizer_config(path)
    norm = Normalizer(cfg)
    assert norm.normalize("3 pt") == "trê part"


def test_load_config_yaml(tmp_path: Path) -> None:
    pytest.importorskip("yaml")
    data = {
        "numbers_map": {"4": "cuatri"},
        "units_map": {"km": "chilometr"},
    }
    path = tmp_path / "norm.yml"
    import yaml  # type: ignore[import-untyped]

    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    cfg = load_normalizer_config(path)
    norm = Normalizer(cfg)
    assert norm.normalize("4 km") == "cuatri chilometr"
