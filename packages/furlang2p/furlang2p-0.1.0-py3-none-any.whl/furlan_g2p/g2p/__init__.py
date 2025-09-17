"""G2P module (skeleton)."""

from __future__ import annotations

from .lexicon import Lexicon
from .phonemizer import G2PPhonemizer
from .rules import PhonemeRules

__all__ = ["Lexicon", "PhonemeRules", "G2PPhonemizer"]
