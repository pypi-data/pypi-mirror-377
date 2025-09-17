"""Sentence and word tokenization utilities."""

from __future__ import annotations

import re

from ..config.schemas import TokenizerConfig
from ..core.interfaces import ITokenizer

_WORD_RE = re.compile(r"[a-zà-öø-ÿç0-9'’]+|_{1,2}", re.IGNORECASE)


class Tokenizer(ITokenizer):
    """Sentence and word tokenizer.

    Sentences are split on ``.``, ``!`` and ``?`` while honouring abbreviations
    that should *not* trigger a boundary (e.g. ``sig.``).  Words are extracted
    as contiguous alphanumeric sequences (including accented letters and
    apostrophes); pause markers ``_`` and ``__`` are preserved as standalone
    tokens.

    Examples
    --------
    >>> cfg = TokenizerConfig(abbrev_no_split={"sig"})
    >>> t = Tokenizer(cfg)
    >>> t.split_sentences("Al è rivât il Sig. Bepo. O ven?")
    ['Al è rivât il Sig. Bepo.', 'O ven?']
    >>> t.split_words("L’aghe __ e je freda _")
    ["l'aghe", '__', 'e', 'je', 'freda', '_']
    """

    def __init__(self, config: TokenizerConfig | None = None) -> None:
        self.config = config or TokenizerConfig()

    def split_sentences(self, text: str) -> list[str]:
        """Split ``text`` into sentences.

        Parameters
        ----------
        text:
            Raw text string.

        Returns
        -------
        list[str]
            Sentence fragments including their terminal punctuation.
        """

        sentinel = "\uffff"  # unlikely char used as temporary placeholder
        work = text.strip()
        for abbr in self.config.abbrev_no_split:
            pattern = re.compile(rf"\b{re.escape(abbr)}\.", re.IGNORECASE)
            work = pattern.sub(lambda m: m.group(0).replace(".", sentinel), work)
        sentences = [s.replace(sentinel, ".") for s in re.split(r"(?<=[.!?])\s+", work) if s]
        return sentences

    def split_words(self, sentence: str) -> list[str]:
        """Split a ``sentence`` into word tokens.

        Parameters
        ----------
        sentence:
            Sentence to tokenize.

        Returns
        -------
        list[str]
            Lowercase word tokens without punctuation.
        """

        s = sentence.replace("’", "'").lower()
        return _WORD_RE.findall(s)


__all__ = ["Tokenizer"]
