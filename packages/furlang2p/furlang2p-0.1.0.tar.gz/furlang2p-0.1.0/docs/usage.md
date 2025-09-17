# Usage guide

This guide shows how to run the library components and customise their behaviour.

## Pipeline API

```python
from furlan_g2p.services import PipelineService

pipe = PipelineService()
norm, phonemes = pipe.process_text("Cjase")
print(norm)      # cjase
print(phonemes)  # ['ˈc', 'a', 'z', 'e']
```

Call ``process_csv`` to phonemise an LJSpeech ``metadata.csv`` file:

```python
pipe.process_csv("metadata.csv", "out.csv")
```

## Normalisation rules

Load replacement maps and pause markers from JSON or YAML files and feed them to
:class:`Normalizer`:

```python
from furlan_g2p.config import load_normalizer_config
from furlan_g2p.normalization import Normalizer

cfg = load_normalizer_config("norm_rules.yml")
print(Normalizer(cfg).normalize("1964 kg"))
# -> mil nûfcent e sessantecuatri chilogram
```

## Tokenizer configuration

Custom abbreviations that should not end a sentence can be stored externally:

```python
from furlan_g2p.config import load_tokenizer_config
from furlan_g2p.tokenization import Tokenizer

cfg = load_tokenizer_config("tok_rules.yml")
print(Tokenizer(cfg).split_sentences("Al è rivât il Sig. Bepo. O ven?"))
# -> ['Al è rivât il Sig. Bepo.', 'O ven?']
```

## CLI

The ``furlang2p`` command groups several subcommands:

```bash
furlang2p normalize "CJASE 1964 kg"      # text normalisation
furlang2p g2p "Cjase"                    # phoneme sequence
furlang2p phonemize-csv --in metadata.csv --out out.csv
```
