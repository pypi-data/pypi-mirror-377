"""Minimal PipelineService demo."""

from __future__ import annotations

from furlan_g2p.services import PipelineService


def main() -> None:
    """Run a short text through the full pipeline and print results."""
    pipe = PipelineService()
    norm, phonemes = pipe.process_text("Cjase 1964 kg")
    print(norm)
    print(" ".join(phonemes))


if __name__ == "__main__":
    main()
