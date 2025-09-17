"""Property tests for :class:`PhonemeRules`."""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from hypothesis import given as _given  # type: ignore[import-not-found,unused-ignore]
from hypothesis import strategies as st  # type: ignore[import-not-found,unused-ignore]

from furlan_g2p.g2p.rules import PhonemeRules

F = TypeVar("F", bound=Callable[..., Any])


def given(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], _given(*args, **kwargs))


ALPHABET = "abcçdefghijlmnoprstuvzâêîôûàèìòù"
IPA_CHARS = set("abcdefhijklmnoprstuvzàèìòùɟɲʃʒʎːˈɛɔg")


@given(st.text(alphabet=ALPHABET, min_size=1, max_size=10))
def test_outputs_are_ipa_only(s: str) -> None:
    eng = PhonemeRules()
    out = "".join(eng.apply(s))
    assert all(ch in IPA_CHARS for ch in out)
