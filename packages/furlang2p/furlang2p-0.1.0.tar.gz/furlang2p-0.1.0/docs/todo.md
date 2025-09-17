# Roadmap

## High Priority
- **Expand grapheme‑to‑phoneme coverage**
  - Implementation: grow `seed_lexicon.tsv`, extend `PhonemeRules` for additional digraphs and dialectal variation, validate against `PHONEME_INVENTORY`.
  - Testing: add golden pronunciations under `tests/data/` and property tests for new rules.
- **Refine phonology components**
  - Implementation: improve `Syllabifier` cluster handling and enhance `StressAssigner` with secondary stress and vowel reduction rules.
  - Testing: extend `tests/test_phonology_refined.py` and add edge‑case fixtures.
- **Comprehensive test suite**
  - Implementation: broaden CLI and pipeline tests, create fixtures for configuration loading.
  - Testing: run `ruff`, `black`, `mypy` and `pytest` locally and in CI.

## Medium Priority
- **Augment normalisation rules**
  - Implementation: support locale‑specific number formats and richer abbreviation and unit tables loaded from config files.
  - Testing: configuration round‑trip tests and examples covering numeric edge cases.
- **Configurable tokenisation**
  - Implementation: allow external patterns for sentence boundaries and pause markers; support abbreviations with trailing digits.
  - Testing: add parametrised tests in `tests/test_tokenizer.py`.
- **Phoneme inventory management**
  - Implementation: expose inventory differences between dialects and surface warnings for unknown symbols.
  - Testing: verify inventory errors with dedicated unit tests.

## Nice to Have
- **Advanced CLI features**
  - Implementation: progress reporting for CSV phonemisation, streaming mode and plugin registration for custom pipeline stages.
  - Testing: snapshot tests for CLI output and large‑file smoke tests.
- **Documentation tooling**
  - Implementation: auto‑generate API docs and publish the `docs/` tree to a static site.
  - Testing: build documentation in CI to catch broken links or formatting issues.
