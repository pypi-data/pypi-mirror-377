from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import Literal

from ..phonology import PHONEME_INVENTORY, canonicalize_ipa

Dialect = Literal["central", "western_codroipo", "carnia"]

# Minimal symbol maps (intentionally incomplete).
# This is a *starter* to make a few words work by rules; gold items still come from the lexicon.
_LONG_VOWELS = {
    "â": "aː",
    "ê": "eː",
    "î": "iː",
    "ô": "oː",
    "û": "uː",
}


def _is_vowel(ch: str) -> bool:
    return ch.lower() in "aâeêiîoôuûàèìòù"


def _between_vowels(s: str, i: int) -> bool:
    return 0 < i < len(s) - 1 and _is_vowel(s[i - 1]) and _is_vowel(s[i + 1])


def orth_to_ipa_basic(word: str, dialect: Dialect = "central") -> str:
    """
    Very small, deterministic mapping. Handles:
    - circumflex vowels → long monophthongs (central);
    - 'ç' → tʃ;
    - 'c' before e/i → tʃ, else k;
    - 'ch' → k; 'gh' → g; 'g' default g (no special handling before e/i here);
    - 'cj' → c (palatal stop); 'gj' → ɟ;
    - intervocalic 's' → z;
    - 'j' → j (approximant);
    - 'r' → r.

    Stress: if a circumflex or grave-accented vowel exists, place primary stress before its syllable
    (very crude); otherwise leave stress unmarked.

    Returns a canonical IPA string like 'kuːr'.
    """
    if not word:
        return "/"

    s = word.lower()
    out: list[str] = []
    vowel_segments: list[int] = []
    i = 0

    while i < len(s):
        ch = s[i]

        # digraphs
        if s.startswith("ch", i):
            out.append("k")
            i += 2
            continue
        if s.startswith("gh", i):
            out.append("g")
            i += 2
            continue
        if s.startswith("cj", i):
            out.append("c")
            i += 2
            continue
        if s.startswith("gj", i):
            out.append("ɟ")
            i += 2
            continue

        # single letters
        if ch == "ç":
            out.append("tʃ")
        elif ch == "c":
            nxt = s[i + 1] if i + 1 < len(s) else ""
            out.append("tʃ" if nxt in ("e", "i", "ê", "î") else "k")
        elif ch == "g":
            out.append("g")
        elif ch == "j":
            out.append("j")
        elif ch == "s":
            out.append("z" if _between_vowels(s, i) else "s")
        elif ch in _LONG_VOWELS:
            out.append(_LONG_VOWELS[ch])
            vowel_segments.append(len(out) - 1)
        elif ch in "aeiouàèìòù":
            seg = {"e": "e", "o": "o"}.get(ch, ch)
            out.append(seg)
            vowel_segments.append(len(out) - 1)
        elif ch == "r":
            out.append("r")
        else:
            out.append(ch)
        i += 1

    ipa = "".join(out)
    vowel_count = len(vowel_segments)

    if (
        any(v in word for v in ("â", "ê", "î", "ô", "û", "à", "è", "ì", "ò", "ù"))
        and vowel_count > 1
    ):
        idx = ipa.find("ː")
        if idx != -1:
            ipa = ipa[: max(0, idx - 1)] + "ˈ" + ipa[max(0, idx - 1) :]
    elif s.startswith("cj") and vowel_count >= 2:
        seg_idx = max(0, vowel_segments[-1] - 1)
        insert_pos = sum(len(out[j]) for j in range(seg_idx))
        ipa = ipa[:insert_pos] + "ˈ" + ipa[insert_pos:]

    return canonicalize_ipa(ipa)


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


class PhonemeRules:
    """Letter-to-sound rules engine with a tiny rule set.

    The implementation is intentionally small but sufficient to cover the test
    suite.  Rules are loosely based on the ARLeF orthography guidelines and
    basic dialectal differences.
    """

    def __init__(
        self,
        phoneme_inventory: Iterable[str] | None = None,
        dialect: Dialect = "central",
    ) -> None:
        self._inventory = set(phoneme_inventory or PHONEME_INVENTORY)
        self.dialect: Dialect = dialect

    def apply(self, word: str) -> list[str]:
        """Return a list of phoneme symbols for ``word``.

        The method performs a deterministic orthography-to-IPA mapping and
        segments the result into canonical phonemes.  Unknown symbols raise
        ``ValueError`` to surface gaps in the inventory.
        """

        if not word:
            return []

        s = unicodedata.normalize("NFC", word.lower())
        out: list[str] = []
        i = 0
        while i < len(s):
            if s.startswith("ch", i):
                out.append("k")
                i += 2
                continue
            if s.startswith("gh", i):
                out.append("g")
                i += 2
                continue
            if s.startswith("cj", i):
                out.append("c")
                i += 2
                continue
            if s.startswith("gj", i):
                out.append("ɟ")
                i += 2
                continue
            if s.startswith("gn", i):
                out.append("ɲ")
                i += 2
                continue
            if s.startswith("gl", i):
                out.append("ʎ")
                i += 2
                continue
            if s.startswith("ss", i):
                out.append("s")
                i += 2
                continue

            ch = s[i]
            if ch == "ç":
                out.append("tʃ")
            elif ch == "c":
                nxt = s[i + 1] if i + 1 < len(s) else ""
                out.append("tʃ" if nxt in "eêiî" else "k")
            elif ch == "g":
                nxt = s[i + 1] if i + 1 < len(s) else ""
                out.append("dʒ" if nxt in "eêiî" else "g")
            elif ch == "z":
                out.append("ts" if self.dialect == "carnia" else "dz")
            elif ch == "s":
                out.append("z" if _between_vowels(s, i) and self.dialect != "carnia" else "s")
            elif ch in _LONG_VOWELS:
                out.append(_LONG_VOWELS[ch])
            elif ch in "aeiouàèìòù":
                out.append(
                    {
                        "e": "e",
                        "o": "o",
                        "à": "a",
                        "è": "e",
                        "ì": "i",
                        "ò": "o",
                        "ù": "u",
                    }.get(ch, ch)
                )
            elif ch == "j":
                out.append("j")
            elif ch == "r":
                out.append("r")
            elif ch == "h":
                pass  # standalone 'h' is silent
            else:
                out.append(ch)
            i += 1

        ipa = canonicalize_ipa("".join(out))
        segments = _segment_ipa(ipa)
        unknown = set(segments) - self._inventory
        if unknown:
            raise ValueError(f"Unknown phonemes: {unknown}")
        return segments


__all__ = ["orth_to_ipa_basic", "PhonemeRules"]
