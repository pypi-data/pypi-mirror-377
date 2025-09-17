from __future__ import annotations

import csv
from pathlib import Path

from furlan_g2p.services.pipeline import PipelineService


def test_pipeline_against_golden_set() -> None:
    service = PipelineService()
    data_path = Path(__file__).parent / "data" / "pipeline_golden.tsv"
    with data_path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for text, expected_norm, expected_phons in reader:
            norm, phons = service.process_text(text)
            assert norm == expected_norm
            assert " ".join(phons) == expected_phons
