"""Run evaluation scenarios and compute reproducible metrics (report section 3.4).

Three tracks are evaluated:

* access control correctness (KB1-KB3),
* prompt injection detection (KB4-KB6) as a binary classification, and
* the no-middleware baseline (KB7) showing attacks succeed without KMAM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kmam.context import RequestContext, Verdict
from kmam.detection.detector import PromptInjectionDetector
from kmam.detection.rules import RuleFilter, Signal
from kmam.devices.simulator import DeviceSimulator
from kmam.evaluation.scenarios import ControlScenario, TextSample
from kmam.middleware import SecurityMiddleware


@dataclass
class ConfusionMetrics:
    """Binary confusion matrix with derived scores (positive class = injection)."""

    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        denom = self.precision + self.recall
        return 2 * self.precision * self.recall / denom if denom else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tp": self.tp, "fp": self.fp, "tn": self.tn, "fn": self.fn,
            "total": self.total,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
        }


def evaluate_access_control(
    middleware: SecurityMiddleware, scenarios: list[ControlScenario]
) -> dict[str, Any]:
    """Compare the middleware verdict against the expected verdict per scenario."""
    results = []
    correct = 0
    for s in scenarios:
        res = middleware.handle_request(
            session_id=s.session_id,
            device_id=s.device_id,
            action=s.action,
            params=s.params,
            environment=s.environment,
        )
        predicted = res.decision.verdict
        ok = predicted == s.expected
        correct += int(ok)
        results.append({
            "id": s.id,
            "group": s.group,
            "expected": s.expected.value,
            "predicted": predicted.value,
            "stage": res.decision.stage,
            "correct": ok,
        })
    total = len(scenarios)
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "results": results,
    }


def _tally(metrics: ConfusionMetrics, is_injection: bool, predicted: bool) -> None:
    if is_injection and predicted:
        metrics.tp += 1
    elif is_injection and not predicted:
        metrics.fn += 1
    elif not is_injection and predicted:
        metrics.fp += 1
    else:
        metrics.tn += 1


def evaluate_injection_detection(
    detector: PromptInjectionDetector, samples: list[TextSample]
) -> dict[str, Any]:
    """Score detections against the labels, broken down by the deciding tier.

    A deny is treated as 'predicted injection'. Each decision is attributed to the tier
    that produced it (``rule`` or ``llm``), so the report can show which tier caught what.
    """
    overall = ConfusionMetrics()
    by_tier: dict[str, ConfusionMetrics] = {"rule": ConfusionMetrics(), "llm": ConfusionMetrics()}
    results = []
    for sample in samples:
        ctx = RequestContext(session_id="eval", raw_user_request=sample.text)
        decision = detector.detect(ctx)
        predicted = not decision.allowed
        tier = decision.tier or "rule"
        _tally(overall, sample.is_injection, predicted)
        _tally(by_tier.setdefault(tier, ConfusionMetrics()), sample.is_injection, predicted)
        results.append({
            "id": sample.id,
            "group": sample.group,
            "is_injection": sample.is_injection,
            "predicted_injection": predicted,
            "tier": tier,
        })
    return {
        "metrics": overall.to_dict(),
        "by_tier": {tier: m.to_dict() for tier, m in by_tier.items()},
        "results": results,
    }


def analyze_rule_tier(samples: list[TextSample]) -> dict[str, Any]:
    """Evaluate the regex rule tier alone and list the samples it misclassifies.

    This is deterministic (no LLM). It captures where the rule tier is confidently wrong
    so the patterns can be tuned: false positives mean the rules over-filter (block a
    benign text), false negatives mean an injection leaks past the rules as benign.
    Cases marked UNCERTAIN are not counted as errors, since they are escalated to the LLM.
    """
    rule_filter = RuleFilter()
    metrics = ConfusionMetrics()
    escalated = 0
    false_positives = []  # benign text the rules flagged as malicious (over-filtering)
    false_negatives = []  # injection text the rules passed as benign (leak)
    for sample in samples:
        result = rule_filter.inspect(sample.text)
        if result.signal is Signal.UNCERTAIN:
            escalated += 1
            continue
        predicted = result.signal is Signal.MALICIOUS
        _tally(metrics, sample.is_injection, predicted)
        record = {
            "id": sample.id,
            "group": sample.group,
            "text": sample.text,
            "is_injection": sample.is_injection,
            "rule_signal": result.signal.value,
            "rule_reason": result.reason,
        }
        if predicted and not sample.is_injection:
            false_positives.append(record)
        elif not predicted and sample.is_injection:
            false_negatives.append(record)
    return {
        "settled_metrics": metrics.to_dict(),
        "escalated_to_llm": escalated,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def evaluate_baseline(
    middleware: SecurityMiddleware, scenarios: list[ControlScenario]
) -> dict[str, Any]:
    """Run attack scenarios with and without the middleware to compare outcomes."""
    attacks = [s for s in scenarios if s.is_attack]
    bare = DeviceSimulator.from_config()

    executed_without = 0
    blocked_with = 0
    for s in attacks:
        # Without middleware: command goes straight to the device.
        try:
            bare.execute(s.device_id, s.action, s.params)
            executed_without += 1
        except Exception:
            pass
        # With middleware: same request through the pipeline.
        res = middleware.handle_request(
            session_id=s.session_id,
            device_id=s.device_id,
            action=s.action,
            params=s.params,
            environment=s.environment,
        )
        if not res.executed:
            blocked_with += 1

    n = len(attacks)
    return {
        "attacks": n,
        "executed_without_middleware": executed_without,
        "blocked_by_middleware": blocked_with,
        "attack_success_rate_without_middleware": round(executed_without / n, 4) if n else 0.0,
        "attack_success_rate_with_middleware": round((n - blocked_with) / n, 4) if n else 0.0,
    }
