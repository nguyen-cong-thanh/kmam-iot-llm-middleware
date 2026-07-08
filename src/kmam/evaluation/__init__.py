"""Reproducible evaluation of the KMAM middleware (report section 3.4)."""

from kmam.evaluation.runner import (
    ConfusionMetrics,
    analyze_rule_tier,
    evaluate_access_control,
    evaluate_baseline,
    evaluate_injection_detection,
)
from kmam.evaluation.scenarios import (
    ControlScenario,
    TextSample,
    generate_control_scenarios,
    generate_injection_samples,
)

__all__ = [
    "ConfusionMetrics",
    "ControlScenario",
    "TextSample",
    "analyze_rule_tier",
    "evaluate_access_control",
    "evaluate_baseline",
    "evaluate_injection_detection",
    "generate_control_scenarios",
    "generate_injection_samples",
]
