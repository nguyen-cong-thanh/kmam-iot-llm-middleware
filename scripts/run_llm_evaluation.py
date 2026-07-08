"""Compare prompt injection detection across models and datasets (report section 3.4).

For each dataset (the self-made scenarios plus every committed public dataset) the
two-tier detector is evaluated per model (gemma via local Ollama, deepseek via API)
against a rule-only baseline, with a per-tier breakdown and a standalone analysis of the
regex rule tier's mistakes.

DeepSeek needs VPN. gemma runs locally. Large public datasets make many LLM calls on the
uncertain cases, so use --limit-public to bound a run.

    uv run python scripts/run_llm_evaluation.py
    uv run python scripts/run_llm_evaluation.py --models gemma            # local only
    uv run python scripts/run_llm_evaluation.py --limit-public 300        # shorter run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kmam.agent import build_llm_detector
from kmam.detection.detector import PromptInjectionDetector
from kmam.evaluation import (
    analyze_rule_tier,
    evaluate_injection_detection,
    generate_injection_samples,
)
from kmam.evaluation.public_dataset import available_datasets, load_public_injection_samples

RESULTS_DIR = Path("results")


def _collect_datasets(limit_public: int | None) -> dict[str, list]:
    datasets = {"selfmade": generate_injection_samples()}
    for name in available_datasets():
        datasets[name] = load_public_injection_samples(name, limit=limit_public)
    return datasets


def _overall_table(dataset: str, per_model: dict[str, dict]) -> list[str]:
    lines = [
        f"### {dataset}",
        "",
        "| detector | precision | recall | f1 | accuracy | tp | fp | tn | fn |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for model, rep in per_model.items():
        m = rep["metrics"]
        lines.append(
            f"| {model} | {m['precision']} | {m['recall']} | {m['f1']} | {m['accuracy']} "
            f"| {m['tp']} | {m['fp']} | {m['tn']} | {m['fn']} |"
        )
    lines += ["", "| detector | tier | decisions | tp | fp | fn | recall |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for model, rep in per_model.items():
        for tier, m in rep["by_tier"].items():
            if m["total"] == 0:
                continue
            lines.append(
                f"| {model} | {tier} | {m['total']} | {m['tp']} | {m['fp']} "
                f"| {m['fn']} | {m['recall']} |"
            )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=["gemma", "deepseek"])
    parser.add_argument("--limit-public", type=int, default=None)
    args = parser.parse_args()

    datasets = _collect_datasets(args.limit_public)
    print("Datasets: " + ", ".join(f"{n}({len(s)})" for n, s in datasets.items()) + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Deterministic rule-tier error analysis per dataset (no LLM).
    rule_errors = {name: analyze_rule_tier(samples) for name, samples in datasets.items()}
    (RESULTS_DIR / "rule_tier_errors.json").write_text(
        json.dumps(rule_errors, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # report[dataset][model] = {metrics, by_tier, results}
    report: dict[str, dict] = {name: {} for name in datasets}
    detectors = {"rule_only": PromptInjectionDetector()}
    for model in args.models:
        print(f"Building detector for model: {model} ...")
        detectors[model] = build_llm_detector(model)

    for name, samples in datasets.items():
        for model, detector in detectors.items():
            report[name][model] = evaluate_injection_detection(detector, samples)

    (RESULTS_DIR / "llm_comparison.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    out = ["# Injection detection: models x datasets", ""]
    for name in datasets:
        out += _overall_table(name, report[name])
        ra = rule_errors[name]
        out += [
            "",
            f"Rule tier (regex) on {name}: escalated={ra['escalated_to_llm']}, "
            f"false_positives={len(ra['false_positives'])}, "
            f"false_negatives={len(ra['false_negatives'])}",
            "",
        ]
    print("\n".join(out))
    print("Wrote results/llm_comparison.json and results/rule_tier_errors.json")


if __name__ == "__main__":
    main()
