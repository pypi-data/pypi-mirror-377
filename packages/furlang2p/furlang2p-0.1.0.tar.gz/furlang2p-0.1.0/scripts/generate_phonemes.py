#!/usr/bin/env python3
"""Batch phonemize a metadata CSV file using :class:`PipelineService`."""

from __future__ import annotations

import argparse
import sys

from furlan_g2p.services.pipeline import PipelineService


def main() -> None:
    """Phonemize an input CSV and write the result to ``--out``.

    The input file is expected to contain LJSpeech-style rows with at least an
    identifier and the text to phonemize separated by ``--delim``.
    """

    parser = argparse.ArgumentParser(description="Batch phonemize a metadata CSV")
    parser.add_argument("--in", dest="inp", required=True, help="Input metadata CSV")
    parser.add_argument("--out", dest="out", required=True, help="Output CSV path")
    parser.add_argument("--delim", dest="delim", default="|", help="CSV delimiter", metavar="D")
    args = parser.parse_args()

    service = PipelineService()
    try:
        service.process_csv(args.inp, args.out, delimiter=args.delim)
    except FileNotFoundError as e:
        print(f"Missing file: {e.filename}", file=sys.stderr)
        raise SystemExit(1) from e


if __name__ == "__main__":  # pragma: no cover
    main()
