"""Generate the evaluation scenarios and dump them to data/scenarios/ as JSON.

Run with: uv run python scripts/generate_scenarios.py
"""

from __future__ import annotations

import json
from pathlib import Path

from kmam.evaluation import generate_control_scenarios, generate_injection_samples

OUTPUT_DIR = Path("data/scenarios")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    control = [s.to_dict() for s in generate_control_scenarios()]
    samples = [s.to_dict() for s in generate_injection_samples()]

    (OUTPUT_DIR / "control_scenarios.json").write_text(
        json.dumps(control, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "injection_samples.json").write_text(
        json.dumps(samples, indent=2), encoding="utf-8"
    )

    print(f"Wrote {len(control)} control scenarios and {len(samples)} injection samples "
          f"to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
