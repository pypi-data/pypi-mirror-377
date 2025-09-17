"""Syllabification helpers with basic Friulian phonotactics."""

from __future__ import annotations

from collections.abc import Iterable

from ..core.interfaces import ISyllabifier

_VOWELS = set("aeiouɛɔ")


def _is_vowel(ph: str) -> bool:
    """Return ``True`` if ``ph`` is a vowel symbol."""

    return ph[0] in _VOWELS


def _combine_length(phonemes: list[str]) -> list[str]:
    """Merge length markers with the preceding vowel.

    Parameters
    ----------
    phonemes:
        Raw phoneme list possibly containing standalone ``ː`` markers.

    Returns
    -------
    list[str]
        List where long vowels appear as single elements (e.g. ``aː``).
    """

    combined: list[str] = []
    i = 0
    while i < len(phonemes):
        ph = phonemes[i]
        if _is_vowel(ph) and i + 1 < len(phonemes) and phonemes[i + 1] == "ː":
            combined.append(ph + "ː")
            i += 2
        else:
            combined.append(ph)
            i += 1
    return combined


# Allow complex onsets such as ``pr``/``st``/``spl``.
_ALLOWED_ONSETS: set[tuple[str, ...]] = {
    ("p", "r"),
    ("p", "l"),
    ("b", "r"),
    ("b", "l"),
    ("t", "r"),
    ("d", "r"),
    ("k", "r"),
    ("k", "l"),
    ("g", "r"),
    ("g", "l"),
    ("f", "r"),
    ("f", "l"),
    ("s", "p", "r"),
    ("s", "p", "l"),
    ("s", "t", "r"),
    ("s", "k", "r"),
    ("s", "k", "l"),
}


class Syllabifier(ISyllabifier):
    """Syllabifier using onset maximisation and basic clusters.

    Consonant groups between vowels are split so that the maximal permissible
    onset attaches to the following syllable.  Complex clusters such as ``pr``,
    ``str`` or ``scl`` are accepted when listed in ``_ALLOWED_ONSETS``.  Standalone
    length markers are merged with the preceding vowel before processing.

    Examples
    --------
    >>> Syllabifier().syllabify(['o', 'r', 'e', 'l', 'e'])
    [['o'], ['r', 'e'], ['l', 'e']]
    >>> Syllabifier().syllabify(['s', 't', 'r', 'i', 'ɛ'])
    [['s', 't', 'r', 'i'], ['ɛ']]
    """

    def syllabify(self, phonemes: Iterable[str]) -> list[list[str]]:
        """Split ``phonemes`` into a list of syllables."""

        phs = _combine_length(list(phonemes))
        syllables: list[list[str]] = []
        onset: list[str] = []
        i = 0
        while i < len(phs):
            ph = phs[i]
            if _is_vowel(ph):
                nucleus = ph
                i += 1
                cluster: list[str] = []
                while i < len(phs) and not _is_vowel(phs[i]):
                    cluster.append(phs[i])
                    i += 1
                if i < len(phs):
                    split = len(cluster)
                    for size in range(min(3, len(cluster)), 0, -1):
                        cand = tuple(cluster[-size:])
                        if cand in _ALLOWED_ONSETS or size == 1:
                            split = len(cluster) - size
                            break
                    coda = cluster[:split]
                    next_onset = cluster[split:]
                    syllables.append(onset + [nucleus] + coda)
                    onset = next_onset
                else:
                    syllables.append(onset + [nucleus] + cluster)
                    onset = []
            else:
                onset.append(ph)
                i += 1
        if onset:
            if syllables:
                syllables[-1].extend(onset)
            else:
                syllables.append(onset)
        return syllables


__all__ = ["Syllabifier"]
