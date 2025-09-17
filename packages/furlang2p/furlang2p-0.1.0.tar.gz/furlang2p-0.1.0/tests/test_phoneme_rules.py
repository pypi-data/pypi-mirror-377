from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

from hypothesis import given as _given  # type: ignore[import-not-found,unused-ignore]
from hypothesis import strategies as st  # type: ignore[import-not-found,unused-ignore]

from furlan_g2p.g2p.rules import PhonemeRules
from furlan_g2p.phonology import PHONEME_INVENTORY

F = TypeVar("F", bound=Callable[..., Any])


def given(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], _given(*args, **kwargs))


ALPHABET = "abcçdefghijlmnoprstuvzâêîôûàèìòù"


@given(st.text(alphabet=ALPHABET, min_size=1, max_size=10))
def test_rules_output_inventory(s: str) -> None:
    rules = PhonemeRules()
    out = rules.apply(s)
    assert all(p in PHONEME_INVENTORY for p in out)


def test_affricates_and_dialect() -> None:
    rules = PhonemeRules()
    assert rules.apply("zente") == ["dz", "e", "n", "t", "e"]
    carn = PhonemeRules(dialect="carnia")
    assert carn.apply("zente")[0] == "ts"


def test_soft_g_and_palatal() -> None:
    rules = PhonemeRules()
    assert rules.apply("gela")[:2] == ["dʒ", "e"]
    assert rules.apply("gjat") == ["ɟ", "a", "t"]
