"""Offline loader for committed public prompt-injection datasets (KB6).

Datasets are downloaded once by ``scripts/fetch_public_dataset.py`` (normalised to
{"text", "label"} with label 1 = injection) and committed under ``data/external/``. This
loader only reads those local files, so evaluation stays offline and reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path

from kmam.evaluation.scenarios import TextSample

# name -> (source dataset id, committed file name)
PUBLIC_DATASETS: dict[str, tuple[str, str]] = {
    "deepset": ("deepset/prompt-injections", "deepset_prompt_injections.json"),
    "safeguard": ("xTRam1/safe-guard-prompt-injection", "safeguard_prompt_injection.json"),
    "jailbreak": ("jackhhao/jailbreak-classification", "jailbreak_classification.json"),
}

EXTERNAL_DIR = Path(__file__).resolve().parents[3] / "data" / "external"


def dataset_path(name: str) -> Path:
    return EXTERNAL_DIR / PUBLIC_DATASETS[name][1]


def available_datasets() -> list[str]:
    """Names of public datasets whose committed file is present."""
    return [name for name in PUBLIC_DATASETS if dataset_path(name).exists()]


def load_public_injection_samples(
    name: str = "deepset", limit: int | None = None, data_file: str | Path | None = None
) -> list[TextSample]:
    """Load a committed public dataset as :class:`TextSample` objects."""
    path = Path(data_file) if data_file is not None else dataset_path(name)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Fetch it once (with VPN) via: "
            f"uv run python scripts/fetch_public_dataset.py --name {name}"
        )
    source = PUBLIC_DATASETS[name][0] if name in PUBLIC_DATASETS else str(name)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if limit is not None:
        raw = raw[:limit]
    return [
        TextSample(
            id=f"{name}-{i:04d}",
            group=name,
            source=source,
            text=row["text"],
            is_injection=bool(row["label"]),
        )
        for i, row in enumerate(raw)
    ]
