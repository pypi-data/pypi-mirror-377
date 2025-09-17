from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_generate_phonemes_script(tmp_path: Path) -> None:
    inp = tmp_path / "meta.csv"
    inp.write_text("utt0|Cjase\n", encoding="utf-8")
    out = tmp_path / "out.csv"
    script = Path(__file__).resolve().parents[1] / "scripts" / "generate_phonemes.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--in", str(inp), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert out.read_text(encoding="utf-8").strip() == "utt0|cjase|ˈc a z e"
