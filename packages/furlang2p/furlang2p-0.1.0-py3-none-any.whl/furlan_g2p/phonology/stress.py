"""Stress assignment helpers."""

from __future__ import annotations

from ..core.interfaces import IStressAssigner


class StressAssigner(IStressAssigner):
    """Heuristic stress assigner for Friulian.

    The default rule stresses the penultimate syllable, but the implementation
    also accounts for marked accents and long vowels which often indicate a
    stressed final syllable [1] [2].  If a syllable already carries a stress
    marker, it is preserved.

    Examples
    --------
    >>> StressAssigner().assign_stress([['o'], ['r', 'e'], ['l', 'e']])
    [['o'], ['ˈr', 'e'], ['l', 'e']]
    >>> StressAssigner().assign_stress([['p', 'a'], ['t', 'iː']])
    [['p', 'a'], ['ˈt', 'iː']]
    """

    # References
    # ----------
    # [1] ARLeF. (2017). *La grafie uficiâl de lenghe furlane*, §10.
    # [2] Miotti, R. (2002). *Friulian*. Journal of the International
    #     Phonetic Association, 32(2), 249–254.

    def assign_stress(self, syllables: list[list[str]]) -> list[list[str]]:
        """Return ``syllables`` with primary stress markers applied.

        If a syllable already starts with ``ˈ`` the input is returned
        unchanged.  Otherwise the last syllable containing a long vowel
        (``ː``) is stressed.  If no long vowel is found, the penultimate
        syllable receives stress, or the final one in monosyllables.
        """

        if not syllables:
            return []
        out = [list(s) for s in syllables]

        # Respect pre-marked stress
        if any(syl and syl[0].startswith("ˈ") for syl in out):
            return out

        # Long vowel heuristic
        long_idx = None
        for idx, syl in enumerate(out):
            if any("ː" in ph for ph in syl):
                long_idx = idx

        if long_idx is not None:
            out[long_idx][0] = "ˈ" + out[long_idx][0]
            return out

        idx = 0 if len(out) == 1 else len(out) - 2
        out[idx][0] = "ˈ" + out[idx][0]
        return out


__all__ = ["StressAssigner"]
