"""Tests for the evaluation harness (report section 3.4)."""

from kmam.evaluation import (
    ConfusionMetrics,
    evaluate_access_control,
    evaluate_baseline,
    evaluate_injection_detection,
    generate_control_scenarios,
    generate_injection_samples,
)
from kmam.middleware import SecurityMiddleware


def test_scenarios_are_generated():
    control = generate_control_scenarios()
    samples = generate_injection_samples()
    assert any(s.group == "KB1" for s in control)
    assert any(s.is_attack for s in control)
    assert any(s.is_injection for s in samples)
    assert any(not s.is_injection for s in samples)


def test_confusion_metrics_scores():
    m = ConfusionMetrics(tp=4, fp=0, tn=5, fn=1)
    assert m.precision == 1.0
    assert m.recall == 0.8
    assert round(m.f1, 4) == 0.8889
    assert m.accuracy == 0.9


def test_access_control_is_fully_correct():
    mw = SecurityMiddleware.from_config()
    report = evaluate_access_control(mw, generate_control_scenarios())
    # Policies and scenarios are designed to be consistent.
    assert report["accuracy"] == 1.0


def test_injection_detection_has_no_false_positives():
    mw = SecurityMiddleware.from_config()
    report = evaluate_injection_detection(mw.detector, generate_injection_samples())
    metrics = report["metrics"]
    assert metrics["fp"] == 0  # benign requests are not flagged by the rule tier
    assert metrics["recall"] >= 0.8


def test_baseline_shows_attacks_succeed_without_middleware():
    mw = SecurityMiddleware.from_config()
    base = evaluate_baseline(mw, generate_control_scenarios())
    assert base["attacks"] > 0
    assert base["attack_success_rate_without_middleware"] == 1.0
    assert base["attack_success_rate_with_middleware"] == 0.0
