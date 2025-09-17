from __future__ import annotations

from furlan_g2p.phonology.ipa import canonicalize_ipa
from furlan_g2p.phonology.stress import StressAssigner
from furlan_g2p.phonology.syllabifier import Syllabifier


def test_canonicalize_ipa_variants() -> None:
    s = canonicalize_ipa("/t\u0361s d\u0361\u0292 ɹ ʤ ɾ ˊa/")
    assert s == "ts dʒ r dʒ r ˈa"


def test_syllabifier_clusters_and_length() -> None:
    syl = Syllabifier()
    assert syl.syllabify(["s", "t", "r", "i", "ɛ"]) == [["s", "t", "r", "i"], ["ɛ"]]
    assert syl.syllabify(["k", "u", "ː", "r"]) == [["k", "uː", "r"]]


def test_stress_assigner_long_vowel_and_existing() -> None:
    stress = StressAssigner()
    assert stress.assign_stress([["p", "a"], ["t", "iː"]]) == [["p", "a"], ["ˈt", "iː"]]
    pre = [["ˈr", "e"], ["l", "e"]]
    assert stress.assign_stress(pre) == pre
