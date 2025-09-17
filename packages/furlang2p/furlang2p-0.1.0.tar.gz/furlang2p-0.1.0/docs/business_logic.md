# Business Logic

This document details the algorithms and linguistic rules implemented in FurlanG2P. A bibliography for the sources cited here is maintained in [references.md](references.md).

## Normalisation

The normalisation step enforces a canonical textual form that mirrors the spelling rules in the official Friulian orthography [ARLeF 2017](references.md). Key operations include:

- Unicode NFC normalisation and lower‑casing.
- Replacing curly apostrophes with straight ones so contractions match lexicon entries.
- Mapping `, ; :` to the short pause marker `_` and `. ? !` to the long pause marker `__` for downstream prosody hints.
- Expanding measurement units, abbreviations, acronyms and ordinals according to a `NormalizerConfig` that can be loaded from JSON or YAML.
- Rendering numbers up to 999 999 999 999 as Friulian words using the built‑in `number_to_words_fr` utility, whose forms are based on Wiktionary’s cardinal list [Wiktionary](references.md#numbers-and-abbreviations).

## Tokenisation

Tokenisation occurs in two passes. `split_sentences` shields non‑terminal abbreviations with a sentinel character before splitting on sentence‑final punctuation, ensuring that strings such as `dr.` are not treated as sentence boundaries. `split_words` then normalises apostrophes and extracts tokens with a regular expression that preserves underscore pause markers so subsequent modules can retain pause information.

## Grapheme‑to‑Phoneme

The G2P component combines lexicon lookups with rule‑based conversion:

- `Lexicon` supplies IPA transcriptions from `seed_lexicon.tsv`; lookups are NFC‑normalised, lower‑cased and cached with an LRU strategy.
- `PhonemeRules` implements deterministic orthography→IPA mapping derived from the ARLeF guide to Friulian spelling [ARLeF 2017](references.md):
  - digraph handling for sequences such as `ch`, `gh`, `cj`, `gj`, `gn`, `gl` and `ss`.
  - conversion of circumflex vowels to long monophthongs (`â`→`aː`, `î`→`iː`, etc.).
  - contextual voicing of `s` between vowels and dialect‑aware treatment of `z`, following observations by Baroni & Vanelli (2000) [Baroni & Vanelli 2000](references.md).
  - segmentation of the resulting IPA string and validation of each symbol against `PHONEME_INVENTORY` compiled from ARLeF and Miotti (2002) [Miotti 2002](references.md).
- `G2PPhonemizer` queries the lexicon first and falls back to the rule engine; any stress marks present in the input are removed before segmentation so that stress assignment can be applied uniformly later.

## Phonology

Phonological post‑processing standardises and analyses the IPA output:

- `canonicalize_ipa` removes tie bars and normalises variant symbols (`t͡ʃ`→`tʃ`, `ɹ`→`r`, etc.) to ease downstream processing.
- `Syllabifier` merges standalone length marks with the preceding vowel and applies onset maximisation using a whitelist of allowable clusters described by Miotti (2002) [Miotti 2002](references.md) and Roseano & Finco (2021) [Roseano & Finco 2021](references.md).
- `StressAssigner` honours pre‑marked stress; otherwise it stresses the last long vowel or, if none, the penultimate syllable, reflecting the generalisations noted by Baroni & Vanelli (2000) [Baroni & Vanelli 2000](references.md).

## Pipeline

`PipelineService` orchestrates the modules in the sequence normalisation → sentence split → word split → G2P → syllabification → stress assignment and returns the normalised text together with the final phoneme sequence, enabling batch or interactive processing through the CLI.
