from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from furlan_g2p.cli.app import cli


def test_cli_normalize() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["normalize", "CJASE", "1964", "kg"])
    assert result.exit_code == 0
    assert result.output.strip() == "cjase mil nûfcent e sessantecuatri chilogram"


def test_cli_g2p() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["g2p", "Cjase"])
    assert result.exit_code == 0
    assert result.output.strip() == "ˈc a z e"


def test_cli_phonemize_csv(tmp_path: Path) -> None:
    inp = tmp_path / "meta.csv"
    inp.write_text("utt0|Cjase\n", encoding="utf-8")
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["phonemize-csv", "--in", str(inp), "--out", str(out)])
    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").strip() == "utt0|cjase|ˈc a z e"
