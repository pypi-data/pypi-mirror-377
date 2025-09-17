# Project Architecture

FurlanG2P is organised as a set of small, typed modules that compose a text‑to‑phoneme pipeline.

## Module map

| Package | Responsibility | Design notes | Maturity |
| --- | --- | --- | --- |
| `core` | exceptions, abstract interfaces, shared type aliases | interface‑driven design with custom error hierarchy | stable |
| `config` | dataclass configs and JSON/YAML loaders | optional `pyyaml` dependency, type‑checked dataclasses | prototype |
| `normalization` | deterministic text normalisation and number spelling | rules layer extensible via `NormalizerConfig` | prototype |
| `tokenization` | sentence and word tokeniser | regex engine with abbreviation sentinel replacement | prototype |
| `g2p` | seed lexicon, letter‑to‑sound rules and phonemiser | LRU‑cached lookups, dialect flag, inventory validation | experimental |
| `phonology` | IPA canonicaliser, syllabifier and stress assigner | onset‑maximisation, heuristic stress rules | experimental |
| `services` | orchestrating pipeline and simple file I/O | service layer encapsulating pipeline steps | minimal |
| `cli` | `click` entry points and subcommands | thin wrapper over services | minimal |
| `data` | packaged seed lexicon TSV | loaded via `importlib.resources` | seed |
| `docs` | usage, rationale, references and internal docs | kept in sync with source modules | evolving |
| `tests` | regression and property tests | guard implemented behaviour | provisional |

## Architectural patterns

- **Interface driven** – `core.interfaces` defines `INormalizer`, `ITokenizer`, `IG2PPhonemizer`, `ISyllabifier` and `IStressAssigner` so implementations can evolve behind stable APIs.
- **Service layer** – `services.PipelineService` composes normalisation → tokenisation → G2P → phonology into a reusable pipeline.
- **Resource packaging** – `g2p.Lexicon` ships a TSV lexicon inside the wheel and accesses it with `importlib.resources`.
- **Configuration via dataclasses** – normalisation and tokenisation behaviour is configured through dataclasses loaded from JSON or YAML files.
