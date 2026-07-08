"""Compare prompt injection detection across escalation strategies and datasets (report section 3.4).

For each dataset (the self-made scenarios plus every committed public dataset) the
two-tier detector (LLM tier = deepseek via API) is evaluated against a rule-only
baseline, with a per-tier breakdown and a standalone analysis of the regex rule tier's
mistakes.

DeepSeek needs VPN. Results for each approach are written to a separate file
(results/llm_comparison_A.json / _B.json); a run merges in only the models it evaluated.

Approach A escalates only uncertain cases to the LLM; approach B escalates every case the
rule tier does not block (many more LLM calls), so use --limit-public to bound a run.

    uv run python scripts/run_llm_evaluation.py --approach A
    uv run python scripts/run_llm_evaluation.py --approach B
    uv run python scripts/run_llm_evaluation.py --approach B --limit-public 300
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
    parser.add_argument("--models", nargs="*", default=["deepseek"])
    parser.add_argument("--limit-public", type=int, default=None)
    parser.add_argument(
        "--approach", choices=["A", "B"], default="A",
        help="A = escalate only uncertain cases; B = escalate every non-blocked case",
    )
    args = parser.parse_args()
    escalate_all = args.approach == "B"

    datasets = _collect_datasets(args.limit_public)
    print("Datasets: " + ", ".join(f"{n}({len(s)})" for n, s in datasets.items()) + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Deterministic rule-tier error analysis per dataset (no LLM).
    rule_errors = {name: analyze_rule_tier(samples) for name, samples in datasets.items()}
    (RESULTS_DIR / "rule_tier_errors.json").write_text(
        json.dumps(rule_errors, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # report[dataset][model] = {metrics, by_tier, results, timing}. Results for each
    # approach are written to a separate file (llm_comparison_A.json / _B.json), so runs
    # of different approaches or models never overwrite each other.
    report: dict[str, dict] = {name: {} for name in datasets}
    detectors = {"rule_only": PromptInjectionDetector()}
    for model in args.models:
        print(f"Building detector: {model} (approach {args.approach}, escalate_all={escalate_all}) ...")
        detectors[model] = build_llm_detector(model, escalate_all=escalate_all)

    def make_progress(model: str, dataset: str):
        def cb(ev: dict) -> None:
            r = ev["running"]
            s = ev["sample"]
            label = "INJ" if s.is_injection else "ben"
            pred = "INJ" if ev["predicted"] else "ben"
            mark = "OK" if (s.is_injection == ev["predicted"]) else "XX"
            print(
                f"  [{model}/{dataset} {ev['index']}/{ev['total']}] {mark} "
                f"label={label} pred={pred} tier={ev['tier']} "
                f"{ev['elapsed_ms']:.0f}ms  acc={r.accuracy:.3f} f1={r.f1:.3f} "
                f"| {s.text[:60]!r}",
                flush=True,
            )
        return cb

    for name, samples in datasets.items():
        for model, detector in detectors.items():
            print(f"\n--- {model} on {name} ({len(samples)} samples) ---", flush=True)
            rep = evaluate_injection_detection(
                detector, samples, progress=make_progress(model, name)
            )
            report[name][model] = rep
            t = rep["timing"]
            print(
                f"--- {model}/{name} done: {t['total_seconds']}s total, "
                f"{t['avg_ms_per_sample']}ms/sample ---",
                flush=True,
            )

    # Merge into this approach's file so separate runs (of different approaches or
    # model sets) do not clobber each other; only the models run now are updated.
    out_file = RESULTS_DIR / f"llm_comparison_{args.approach}.json"
    merged: dict[str, dict] = {}
    if out_file.exists():
        try:
            merged = json.loads(out_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            merged = {}
    for name, per_model in report.items():
        merged.setdefault(name, {}).update(per_model)
    out_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

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
    print(f"Wrote {out_file} and results/rule_tier_errors.json")


if __name__ == "__main__":
    main()
