"""PromptInjectionDetector (FR4): two-tier detection orchestrator.

The rule filter (tier 1) always makes the confident block decision cheaply. Which of the
remaining (non-blocked) cases are sent to the LLM tier is governed by ``escalate_all``:

* ``escalate_all=False`` (approach A): only the UNCERTAIN cases are escalated. The rule
  tier's "benign" verdict is trusted as final, so few requests hit the LLM (cheap, but
  low recall since the rule tier misses subtle injections).
* ``escalate_all=True`` (approach B): every non-blocked case (benign and uncertain) is
  re-checked by the LLM, because the rule tier's "benign" is low-recall and cannot be
  trusted. Much higher recall, at the cost of an LLM call on nearly every request.

When no classifier is configured, ``uncertain_default`` governs the uncertain cases so
the detector can also run in a reproducible rule-only mode.
"""

from __future__ import annotations

from kmam.context import Decision, RequestContext, Verdict
from kmam.detection.llm_classifier import LLMClassifier
from kmam.detection.rules import RuleFilter, Signal

STAGE = "prompt_injection"


def _tagged(decision: Decision, tier: str) -> Decision:
    """Record which tier ("rule" or "llm") produced the decision."""
    decision.tier = tier
    return decision


class PromptInjectionDetector:
    """Combines the rule filter and the optional LLM classifier."""

    def __init__(
        self,
        rule_filter: RuleFilter | None = None,
        llm_classifier: LLMClassifier | None = None,
        uncertain_default: Verdict = Verdict.ALLOW,
        escalate_all: bool = False,
    ) -> None:
        self.rule_filter = rule_filter or RuleFilter()
        self.llm_classifier = llm_classifier
        self.uncertain_default = uncertain_default
        self.escalate_all = escalate_all

    def _text(self, ctx: RequestContext) -> str:
        return ctx.raw_user_request or ""

    def detect(self, ctx: RequestContext) -> Decision:
        result = self.rule_filter.inspect(self._text(ctx))

        # Tier 1 makes the confident block decision without spending an LLM call.
        if result.signal is Signal.MALICIOUS:
            return _tagged(Decision.deny(STAGE, f"rule tier: {result.reason}"), "rule")

        # Decide whether this non-blocked case is escalated to the LLM tier.
        escalate = self.escalate_all or result.signal is Signal.UNCERTAIN
        if escalate and self.llm_classifier is not None:
            classification = self.llm_classifier.classify(self._text(ctx))
            if classification.is_injection:
                return _tagged(Decision.deny(STAGE, classification.reason), "llm")
            return _tagged(Decision.allow(STAGE, classification.reason), "llm")

        # Not escalated (or no LLM configured): fall back to the rule-tier verdict.
        if result.signal is Signal.BENIGN:
            return _tagged(Decision.allow(STAGE, "rule tier: no injection signal"), "rule")
        if self.uncertain_default is Verdict.DENY:
            return _tagged(Decision.deny(STAGE, "uncertain and no classifier available"), "rule")
        return _tagged(
            Decision.allow(STAGE, "uncertain, allowed by default (rule-only mode)"), "rule"
        )
