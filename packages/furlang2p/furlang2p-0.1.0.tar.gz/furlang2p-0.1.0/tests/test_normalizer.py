"""Basic tests for the :class:`Normalizer`."""

import unicodedata
from collections.abc import Callable
from typing import Any, TypeVar, cast

from hypothesis import given as _given  # type: ignore[import-not-found,unused-ignore]
from hypothesis import strategies as st  # type: ignore[import-not-found,unused-ignore]

from furlan_g2p.normalization.normalizer import Normalizer

F = TypeVar("F", bound=Callable[..., Any])


def given(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], _given(*args, **kwargs))


norm = Normalizer()


def test_apostrophes_and_punctuation() -> None:
    text = "L’cjase, ‘bêle’!"
    assert norm.normalize(text) == "l'cjase _ 'bêle' __"


def test_nfc_normalization() -> None:
    # "a" + COMBINING CIRCUMFLEX should collapse to single code point
    text = "a\u0302"
    out = norm.normalize(text)
    assert out == "â"
    # ensure the output is NFC
    assert unicodedata.is_normalized("NFC", out)


ALPHABET = "abcçdefghilmnopqrstuvzâêîôûàèìòù'’ \t.,!?;:"


@given(st.text(alphabet=ALPHABET, max_size=20))
def test_idempotence(s: str) -> None:
    out1 = norm.normalize(s)
    out2 = norm.normalize(out1)
    assert out2 == out1
