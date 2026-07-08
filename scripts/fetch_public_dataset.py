"""One-time fetch of public prompt-injection datasets (KB6).

Run this ONCE per dataset, with VPN enabled (the Hugging Face datasets-server may be
blocked otherwise). Each dataset is normalised to a list of {"text", "label"} with
label 1 = injection / 0 = benign, and written under data/external/ to be committed and
read offline by kmam.evaluation.public_dataset. The evaluation never fetches over the
network.

Run with:
    uv run python scripts/fetch_public_dataset.py --name all
    uv run python scripts/fetch_public_dataset.py --name safeguard
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import requests

ROWS_URL = "https://datasets-server.huggingface.co/rows"
OUTPUT_DIR = Path("data/external")

# Each preset maps a dataset to how its columns are normalised. ``positive`` is the raw
# label value that means "injection".
PRESETS: dict[str, dict] = {
    "deepset": {
        "dataset": "deepset/prompt-injections",
        "split": "test", "text_col": "text", "label_col": "label",
        "positive": "1", "out": "deepset_prompt_injections.json",
    },
    "safeguard": {
        "dataset": "xTRam1/safe-guard-prompt-injection",
        "split": "test", "text_col": "text", "label_col": "label",
        "positive": "1", "out": "safeguard_prompt_injection.json",
    },
    "jailbreak": {
        "dataset": "jackhhao/jailbreak-classification",
        "split": "test", "text_col": "prompt", "label_col": "type",
        "positive": "jailbreak", "out": "jailbreak_classification.json",
    },
}


def _fetch_rows(dataset: str, split: str) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        resp = requests.get(
            ROWS_URL,
            params={"dataset": dataset, "config": "default", "split": split,
                    "offset": offset, "length": 100},
            timeout=60,
        )
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("rows", [])
        if not batch:
            break
        rows.extend(item["row"] for item in batch)
        offset += len(batch)
        if offset >= payload.get("num_rows_total", offset):
            break
    return rows


def fetch_one(name: str) -> None:
    cfg = PRESETS[name]
    raw = _fetch_rows(cfg["dataset"], cfg["split"])
    positive = str(cfg["positive"])
    normalised = [
        {"text": row[cfg["text_col"]],
         "label": 1 if str(row[cfg["label_col"]]) == positive else 0}
        for row in raw
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / cfg["out"]
    out_path.write_text(json.dumps(normalised, ensure_ascii=False, indent=2), encoding="utf-8")

    dist = Counter(r["label"] for r in normalised)
    print(f"[{name}] {cfg['dataset']} ({cfg['split']}): {len(normalised)} rows "
          f"-> injection={dist[1]}, benign={dist[0]} -> {out_path}")
    # Show one example per class so the label mapping can be verified by eye.
    for lbl in (1, 0):
        ex = next((r["text"] for r in normalised if r["label"] == lbl), None)
        if ex is not None:
            print(f"    label={lbl} example: {ex[:90]!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", choices=[*PRESETS, "all"], default="all")
    args = parser.parse_args()
    names = list(PRESETS) if args.name == "all" else [args.name]
    for name in names:
        fetch_one(name)


if __name__ == "__main__":
    main()
