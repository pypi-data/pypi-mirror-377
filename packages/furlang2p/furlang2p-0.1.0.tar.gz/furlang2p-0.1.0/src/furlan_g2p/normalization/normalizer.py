"""Text normalization utilities (skeleton)."""

from __future__ import annotations

import re
import unicodedata
from typing import Final

from ..config.schemas import NormalizerConfig
from ..core.exceptions import NormalizationError  # noqa: F401
from ..core.interfaces import INormalizer

_APOSTROPHES_RE: Final = re.compile("[\u2019\u2018\u02bc]")

# ---------------------------------------------------------------------------
# Number to words conversion (0–999 999 999 999)
# ---------------------------------------------------------------------------

_CARD_0_19: Final[dict[int, str]] = {
    0: "zeru",
    1: "un",
    2: "doi",
    3: "trê",
    4: "cuatri",
    5: "cinc",
    6: "sîs",
    7: "siet",
    8: "vot",
    9: "nûf",
    10: "dîs",
    11: "undis",
    12: "dodis",
    13: "tredis",
    14: "cutuardis",
    15: "cuindis",
    16: "sedis",
    17: "disesiet",
    18: "disevot",
    19: "disenûf",
}

_TENS: Final[dict[int, str]] = {
    20: "vincj",
    30: "trente",
    40: "cuarante",
    50: "cincuante",
    60: "sessante",
    70: "setante",
    80: "otante",
    90: "nonante",
}

_UNITS: Final = [
    (1_000_000_000, "miliart", "miliarts"),
    (1_000_000, "milion", "milions"),
    (1000, "mil", "mil"),
]


def _card_u99(n: int) -> str:
    if n < 20:
        return _CARD_0_19[n]
    tens, unit = divmod(n, 10)
    return _TENS[tens * 10] if unit == 0 else f"{_TENS[tens * 10]}{_CARD_0_19[unit]}"


def _card_u999(n: int) -> str:
    if n < 100:
        return _card_u99(n)
    hundreds, rest = divmod(n, 100)
    cent_part = "cent" if hundreds == 1 else f"{_CARD_0_19[hundreds]}cent"
    if rest == 0:
        return cent_part
    if rest < 100:
        return f"{cent_part} e {_card_u99(rest)}"
    return f"{cent_part} {_card_u999(rest)}"


def number_to_words_fr(n: int) -> str:
    """Convert an integer to Friulian words.

    Parameters
    ----------
    n:
        Number between 0 and 999 999 999 999.

    Returns
    -------
    str
        The number spelled out in Friulian. Out-of-range values are returned as
        their decimal string.

    Examples
    --------
    >>> number_to_words_fr(2004)
    'doi mil e cuatri'
    >>> number_to_words_fr(1964)
    'mil nûfcent e sessantecuatri'
    """

    if not 0 <= n <= 999_999_999_999:
        return str(n)
    if n < 1000:
        return _card_u999(n)
    parts: list[str] = []
    remainder = n
    for value, singular, plural in _UNITS:
        qty, remainder = divmod(remainder, value)
        if qty == 0:
            continue
        if value == 1000:
            part = "mil" if qty == 1 else f"{_card_u999(qty)} mil"
        else:
            base = "un" if qty == 1 else _card_u999(qty)
            label = singular if qty == 1 else plural
            part = f"{base} {label}"
        parts.append(part)
    if remainder:
        rem_words = _card_u999(remainder)
        if remainder < 100:
            return f"{' '.join(parts)} e {rem_words}"
        parts.append(rem_words)
    return " ".join(parts)


# Default cardinals allow overriding specific forms in configuration.
_DEFAULT_NUMBERS: Final[dict[str, str]] = {str(k): v for k, v in _CARD_0_19.items()}


class Normalizer(INormalizer):
    """Simple text normalizer with basic expansion rules.

    The normalizer lowercases text, converts curly apostrophes to straight ones,
    maps punctuation to pause markers and replaces numbers, abbreviations,
    acronyms and units according to :class:`NormalizerConfig`. Numbers not
    explicitly mapped are spelled out in Friulian up to 999 999 999 999.

    Examples
    --------
    >>> Normalizer().normalize("1964 kg, Sig.")
    'mil nûfcent e sessantecuatri chilogram _ siôr'
    """

    def __init__(self, config: NormalizerConfig | None = None) -> None:
        self.config = config or NormalizerConfig()
        self._numbers_map = {**_DEFAULT_NUMBERS, **self.config.numbers_map}

    def _replace_token(self, token: str) -> str:
        token = self.config.abbreviations_map.get(token, token)
        token = self.config.acronyms_map.get(token, token)
        token = self.config.units_map.get(token, token)
        if token in self._numbers_map:
            token = self._numbers_map[token]
        elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+|\d+", token):
            token = number_to_words_fr(int(token.replace(".", "")))
        token = self.config.ordinal_map.get(token, token)
        return token

    def normalize(self, text: str) -> str:
        """Normalize raw input text into a canonical, speakable form.

        Parameters
        ----------
        text:
            Raw input text.

        Returns
        -------
        str
            Normalized text.

        Raises
        ------
        NormalizationError
            If the text cannot be normalized.
        """

        if not isinstance(text, str):  # pragma: no cover - defensive programming
            raise NormalizationError("Input must be a string")

        s = unicodedata.normalize("NFC", text)
        s = _APOSTROPHES_RE.sub("'", s)
        s = re.sub(r"[,;:]", f" {self.config.pause_short} ", s)
        s = re.sub(r"[.?!]", f" {self.config.pause_long} ", s)
        tokens = [t for t in re.split(r"\s+", s.strip()) if t]
        out_tokens: list[str] = []
        for raw in tokens:
            token = raw.lower()
            if token in {self.config.pause_short, self.config.pause_long}:
                out_tokens.append(token)
                continue
            out_tokens.append(self._replace_token(token))
        return " ".join(out_tokens)


__all__ = ["Normalizer"]
