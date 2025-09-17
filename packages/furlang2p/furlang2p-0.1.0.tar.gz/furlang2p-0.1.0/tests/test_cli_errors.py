from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from furlan_g2p.cli.app import cli


def test_normalize_requires_input() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["normalize"])
    assert result.exit_code != 0
    assert "No input provided" in result.output


def test_normalize_conflicting_sources(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text("cjase", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli, ["normalize", "--in", str(src), "Cjase"])
    assert result.exit_code != 0
    assert "Provide either TEXT or --in" in result.output


def test_phonemize_csv_missing_file(tmp_path: Path) -> None:
    out = tmp_path / "o.csv"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["phonemize-csv", "--in", str(tmp_path / "missing.csv"), "--out", str(out)],
    )
    assert result.exit_code != 0
    assert "Could not open file" in result.output
