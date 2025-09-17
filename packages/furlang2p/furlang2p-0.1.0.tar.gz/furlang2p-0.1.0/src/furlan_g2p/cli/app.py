"""Command-line interface for FurlanG2P (skeleton)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from ..g2p.lexicon import Lexicon
from ..g2p.rules import PhonemeRules
from ..normalization.normalizer import Normalizer
from ..phonology import canonicalize_ipa
from ..services.io_service import IOService
from ..services.pipeline import PipelineService
from ..tokenization.tokenizer import Tokenizer

_NORMALIZER = Normalizer()
_LEXICON = Lexicon.load_seed()
_RULES = PhonemeRules()
_TOKENIZER = Tokenizer()
_IO = IOService()


def _split_apostrophes(token: str) -> list[str]:
    """Split ``token`` on apostrophes while keeping them as separate elements."""

    parts: list[str] = []
    start = 0
    for idx, ch in enumerate(token):
        if ch == "'":
            if start < idx:
                parts.append(token[start:idx])
            parts.append("'")
            start = idx + 1
    if start < len(token):
        parts.append(token[start:])
    return parts


def _is_pause(token: str) -> bool:
    """Return ``True`` if ``token`` consists solely of underscores."""

    return bool(token) and set(token) <= {"_"}


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """FurlanG2P command-line interface (skeleton)."""
    # click requires a function body
    pass


@cli.command("normalize")
@click.option("--in", "inp", type=click.Path(exists=True, dir_okay=False), help="Input text file.")
@click.option(
    "--out",
    "out",
    type=click.Path(dir_okay=False),
    help="Write output to file instead of stdout.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["plain", "json"]),
    default="plain",
    show_default=True,
    help="Output format.",
)
@click.argument("text", nargs=-1)
def cmd_normalize(inp: str | None, out: str | None, fmt: str, text: tuple[str, ...]) -> None:
    """Normalize ``text`` and emit the result."""

    if inp and text:
        raise click.UsageError("Provide either TEXT or --in, not both")
    if not inp and not text:
        raise click.UsageError("No input provided")

    service = PipelineService()
    raw = _IO.read_text(inp) if inp else " ".join(text)
    norm = service.normalizer.normalize(raw)
    out_data = json.dumps({"normalized": norm}, ensure_ascii=False) if fmt == "json" else norm
    if out:
        _IO.write_text(out, out_data)
    else:
        click.echo(out_data)


@cli.command("g2p")
@click.option("--in", "inp", type=click.Path(exists=True, dir_okay=False), help="Input text file.")
@click.option(
    "--out",
    "out",
    type=click.Path(dir_okay=False),
    help="Write output to file instead of stdout.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["plain", "json"]),
    default="plain",
    show_default=True,
    help="Output format.",
)
@click.option("--sep", default=" ", show_default=True, help="Phoneme separator for plain format.")
@click.argument("text", nargs=-1)
def cmd_g2p(inp: str | None, out: str | None, fmt: str, sep: str, text: tuple[str, ...]) -> None:
    """Convert ``text`` to a phoneme sequence."""

    if inp and text:
        raise click.UsageError("Provide either TEXT or --in, not both")
    if not inp and not text:
        raise click.UsageError("No input provided")

    service = PipelineService()
    raw = _IO.read_text(inp) if inp else " ".join(text)
    norm, phons = service.process_text(raw)
    out_data = (
        json.dumps({"normalized": norm, "phonemes": phons}, ensure_ascii=False)
        if fmt == "json"
        else sep.join(phons)
    )
    if out:
        _IO.write_text(out, out_data)
    else:
        click.echo(out_data)


@cli.command("phonemize-csv")
@click.option("--in", "inp", required=True, help="Input metadata CSV (LJSpeech-like).")
@click.option("--out", "out", required=True, help="Output CSV with phonemes added.")
@click.option("--delim", "delim", default="|", show_default=True, help="CSV delimiter.")
def cmd_phonemize_csv(inp: str, out: str, delim: str) -> None:
    """Batch phonemize an LJSpeech-style CSV file."""

    service = PipelineService()
    try:
        service.process_csv(inp, out, delimiter=delim)
    except FileNotFoundError as e:  # pragma: no cover - simple passthrough
        raise click.FileError(str(Path(e.filename))) from e
    except Exception as e:  # pragma: no cover - generic error
        raise click.ClickException(str(e)) from e


@cli.command(
    "ipa",
    help="Convert text to IPA using the seed lexicon and rule-based fallback.",
)
@click.option(
    "--rules-only",
    is_flag=True,
    default=False,
    help="Skip lexicon lookup and always use the rule engine.",
)
@click.option(
    "--with-slashes/--no-slashes",
    default=False,
    help="Wrap each token's IPA in /slashes/.",
)
@click.option(
    "--sep",
    default=" ",
    show_default=True,
    help="Separator used to join output tokens.",
)
@click.argument("text", nargs=-1, required=True)
def cmd_ipa(
    text: tuple[str, ...],
    rules_only: bool,
    with_slashes: bool,
    sep: str,
) -> None:
    """Phonemize ``text`` using the stable pipeline components."""

    raw_sentence = " ".join(text)
    norm = _NORMALIZER.normalize(raw_sentence)
    tokens: list[str] = []
    for sent in _TOKENIZER.split_sentences(norm):
        tokens.extend(_TOKENIZER.split_words(sent))
    out_tokens: list[str] = []
    for token in tokens:
        if _is_pause(token):
            out_tokens.append(token)
            continue
        parts = _split_apostrophes(token)
        ipa_parts: list[str] = []
        for part in parts:
            if part == "'":
                ipa_parts.append(part)
                continue
            raw_ipa = (
                "".join(_RULES.apply(part))
                if rules_only
                else (_LEXICON.get(part) or "".join(_RULES.apply(part)))
            )
            ipa = canonicalize_ipa(raw_ipa)
            if with_slashes:
                ipa = f"/{ipa}/"
            ipa_parts.append(ipa)
        out_tokens.append("".join(ipa_parts))
    click.echo(sep.join(out_tokens))


def main() -> None:  # pragma: no cover - small wrapper
    try:
        cli(prog_name="furlang2p")
    except NotImplementedError as e:  # pragma: no cover - placeholder behaviour
        click.echo(f"[FurlanG2P skeleton] {e}", err=True)
        sys.exit(2)


__all__ = ["cli", "main"]
