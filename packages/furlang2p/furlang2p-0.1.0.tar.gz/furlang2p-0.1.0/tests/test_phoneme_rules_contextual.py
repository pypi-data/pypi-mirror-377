"""Smoke tests for the :class:`PhonemeRules` engine.

These are *not* gold pronunciations; they merely check that individual
orthographic contexts map to the expected IPA segments.
"""

import pytest

from furlan_g2p.g2p.rules import PhonemeRules


@pytest.fixture(scope="module")
def eng() -> PhonemeRules:
    return PhonemeRules()


def test_intervocalic_s_and_ss(eng: PhonemeRules) -> None:
    assert "".join(eng.apply("asa")) == "aza"
    assert "".join(eng.apply("assa")) == "asa"


def test_ce_ci_and_c_elsewhere(eng: PhonemeRules) -> None:
    assert "".join(eng.apply("ce")) == "tʃe"
    assert "".join(eng.apply("ci")) == "tʃi"
    assert "".join(eng.apply("ca")) == "ka"


def test_cedilla(eng: PhonemeRules) -> None:
    assert "".join(eng.apply("ça")) == "tʃa"


def test_cj_and_gj(eng: PhonemeRules) -> None:
    assert "".join(eng.apply("cjala")) == "cala"
    assert "".join(eng.apply("gjala")) == "ɟala"


def test_gn(eng: PhonemeRules) -> None:
    assert "".join(eng.apply("agna")) == "aɲa"
    assert "".join(eng.apply("gn")) == "ɲ"
    assert "".join(eng.apply("gno")) == "ɲo"
    assert "".join(eng.apply("ugna")) == "uɲa"
