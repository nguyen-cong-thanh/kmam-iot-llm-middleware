"""PromptInjectionDetector (FR4): two-tier detection orchestrator.

The rule filter (tier 1) settles the clear cases cheaply. Only uncertain cases are
escalated to the LLM classifier (tier 2). When no classifier is configured, the
behaviour for uncertain cases is governed by ``uncertain_default`` so the detector can
also run in a reproducible rule-only mode.
"""

from __future__ import annotations

from kmam.context import Decision, RequestContext, Verdict
from kmam.detection.llm_classifier import LLMClassifier
from kmam.detection.rules import RuleFilter, Signal

STAGE = "prompt_injection"


class PromptInjectionDetector:
    """Combines the rule filter and the optional LLM classifier."""

    def __init__(
        self,
        rule_filter: RuleFilter | None = None,
        llm_classifier: LLMClassifier | None = None,
        uncertain_default: Verdict = Verdict.ALLOW,
    ) -> None:
        self.rule_filter = rule_filter or RuleFilter()
        self.llm_classifier = llm_classifier
        self.uncertain_default = uncertain_default

    def _text(self, ctx: RequestContext) -> str:
        return ctx.raw_user_request or ""

    def detect(self, ctx: RequestContext) -> Decision:
        result = self.rule_filter.inspect(self._text(ctx))

        if result.signal is Signal.MALICIOUS:
            return Decision.deny(STAGE, f"rule tier: {result.reason}")
        if result.signal is Signal.BENIGN:
            return Decision.allow(STAGE, "rule tier: no injection signal")

        # Uncertain: escalate to the LLM tier if available.
        if self.llm_classifier is not None:
            classification = self.llm_classifier.classify(self._text(ctx))
            if classification.is_injection:
                return Decision.deny(STAGE, classification.reason)
            return Decision.allow(STAGE, classification.reason)

        if self.uncertain_default is Verdict.DENY:
            return Decision.deny(STAGE, "uncertain and no classifier available")
        return Decision.allow(STAGE, "uncertain, allowed by default (rule-only mode)")
