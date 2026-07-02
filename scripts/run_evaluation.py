"""Run the full reproducible evaluation and write results to results/.

Uses the rule-only middleware (no LLM) so the core metrics are deterministic. Produces
``results/metrics.json`` and a human-readable ``results/summary.md`` whose tables feed
report section 3.4.

Run with: uv run python scripts/run_evaluation.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kmam.evaluation import (
    evaluate_access_control,
    evaluate_baseline,
    evaluate_injection_detection,
    generate_control_scenarios,
    generate_injection_samples,
)
from kmam.middleware import SecurityMiddleware

RESULTS_DIR = Path("results")


def _render_markdown(report: dict[str, Any]) -> str:
    ac = report["access_control"]
    det = report["injection_detection"]["metrics"]
    base = report["baseline"]
    lines = [
        "# KMAM evaluation summary",
        "",
        "## Access control (KB1-KB3)",
        "",
        f"- Scenarios: {ac['total']}",
        f"- Correct verdicts: {ac['correct']}",
        f"- Accuracy: {ac['accuracy']}",
        "",
        "## Prompt injection detection (KB4-KB6, rule tier)",
        "",
        "| precision | recall | f1 | accuracy | tp | fp | tn | fn |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| {det['precision']} | {det['recall']} | {det['f1']} | {det['accuracy']} "
        f"| {det['tp']} | {det['fp']} | {det['tn']} | {det['fn']} |",
        "",
        "## No-middleware baseline (KB7)",
        "",
        f"- Attack scenarios: {base['attacks']}",
        f"- Attack success rate without middleware: "
        f"{base['attack_success_rate_without_middleware']}",
        f"- Attack success rate with middleware: "
        f"{base['attack_success_rate_with_middleware']}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    middleware = SecurityMiddleware.from_config()
    control = generate_control_scenarios()
    samples = generate_injection_samples()

    report = {
        "access_control": evaluate_access_control(middleware, control),
        "injection_detection": evaluate_injection_detection(middleware.detector, samples),
        "baseline": evaluate_baseline(middleware, control),
    }

    (RESULTS_DIR / "metrics.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (RESULTS_DIR / "summary.md").write_text(_render_markdown(report), encoding="utf-8")

    print(_render_markdown(report))
    print(f"\nWrote results/metrics.json and results/summary.md")


if __name__ == "__main__":
    main()
