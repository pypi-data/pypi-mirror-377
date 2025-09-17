"""IPA helpers for canonical symbol management."""

from __future__ import annotations

import re
import unicodedata

# Common digraphs and symbol variants that should collapse to a canonical
# representation.  The list is based on attested IPA strings in Friulian
# sources [1] and typical transcriber variation.
_REPLACEMENTS: dict[str, str] = {
    "t͡ʃ": "tʃ",  # remove tie bar in affricates
    "d͡ʒ": "dʒ",
    "t͡s": "ts",
    "d͡z": "dz",
    "ʧ": "tʃ",
    "ʤ": "dʒ",
    "ɡ": "g",  # map script g to typographic g
    "ɹ": "r",  # use alveolar trill/tap symbol
    "ɾ": "r",
    "ɳ": "ɲ",
}


def canonicalize_ipa(ipa: str) -> str:
    """Return a canonical representation of ``ipa``.

    The function strips extraneous delimiters, normalises Unicode codepoints and
    collapses known symbol variants so that downstream components operate on a
    stable IPA alphabet.

    - removes leading/trailing slashes and syllable separators ``.``;
    - normalises tie bars and variant affricate symbols to digraphs (``t͡ʃ`` →
      ``tʃ`` etc.);
    - maps tap/approximant ``ɾ``/``ɹ`` to ``r`` and ``ɡ`` to ``g``;
    - normalises ``ɳ`` to ``ɲ``;
    - converts alternative stress marks (``'``/``ˊ``) to ``ˈ``;
    - collapses multiple spaces.

    Parameters
    ----------
    ipa:
        Raw IPA string.

    Returns
    -------
    str
        Canonical IPA string.

    References
    ----------
    [1] ARLeF (2017). *La grafie uficiâl de lenghe furlane*.
    """

    s = unicodedata.normalize("NFC", ipa.strip())
    if s.startswith("/") and s.endswith("/"):
        s = s[1:-1]
    s = s.replace(".", "")
    s = s.replace("͡", "")  # stray tie bars
    for src, tgt in _REPLACEMENTS.items():
        s = s.replace(src, tgt)
    s = re.sub(r"[ˊ']", "ˈ", s)  # unify primary stress marks
    s = re.sub(r"\s+", " ", s).strip()
    return s


__all__ = ["canonicalize_ipa"]
