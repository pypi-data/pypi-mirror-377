"""Grapheme-to-phoneme conversion utilities (skeleton)."""

from __future__ import annotations

from collections.abc import Iterable

from ..core.interfaces import IG2PPhonemizer
from .lexicon import Lexicon
from .rules import PhonemeRules


def _segment_ipa(ipa: str) -> list[str]:
    """Split a canonical IPA string into phoneme symbols."""

    digraphs = ["tʃ", "dʒ", "dz", "ts"]
    segments: list[str] = []
    i = 0
    while i < len(ipa):
        for d in digraphs:
            if ipa.startswith(d, i):
                segments.append(d)
                i += len(d)
                break
        else:
            segments.append(ipa[i])
            i += 1
    return segments


class G2PPhonemizer(IG2PPhonemizer):
    """Phonemizer that combines a lexicon and simple rule fallback.

    Examples
    --------
    >>> G2PPhonemizer().to_phonemes(["cjase"])
    ['c', 'a', 'z', 'e']
    """

    def __init__(self, lexicon: Lexicon | None = None, rules: PhonemeRules | None = None) -> None:
        self.lexicon = lexicon or Lexicon()
        self.rules = rules or PhonemeRules()

    def to_phonemes(self, tokens: Iterable[str]) -> list[str]:
        """Convert token strings into a flat list of phoneme symbols.

        Tokens are looked up in the lexicon; if a token is absent, the
        :class:`PhonemeRules` engine maps the orthography to phonemes as a
        fallback.  Stress marks are stripped before segmentation.
        """

        phonemes: list[str] = []
        for tok in tokens:
            ipa = self.lexicon.get(tok)
            if ipa is not None:
                phonemes.extend(_segment_ipa(ipa.replace("ˈ", "")))
            else:
                phonemes.extend(self.rules.apply(tok))
        return phonemes


__all__ = ["G2PPhonemizer"]
