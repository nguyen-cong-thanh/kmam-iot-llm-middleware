"""Tier 1 of prompt injection detection: a fast rule-based filter.

The filter returns one of three signals (report Figure 3.3): clearly malicious, clearly
benign, or uncertain. Strong patterns map to MALICIOUS, weaker suspicious tokens map to
UNCERTAIN so they can be escalated to the LLM tier, and everything else is BENIGN.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    MALICIOUS = "malicious"
    BENIGN = "benign"
    UNCERTAIN = "uncertain"


@dataclass
class RuleResult:
    signal: Signal
    reason: str = ""


# High-confidence injection patterns.
_STRONG_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+|the\s+|any\s+|your\s+)?(previous|prior|above)\s+(instruction|rule|prompt)",
     "override of prior instructions"),
    (r"disregard\s+.*(instruction|rule|policy|prompt)", "disregard instructions"),
    (r"you\s+are\s+now\s+", "role override"),
    (r"act\s+as\s+(an?\s+)?(admin|administrator|root|system)", "privilege role override"),
    (r"(reveal|leak|exfiltrat\w*|send)\b.*(password|token|api[\s_-]*key|secret|credential)",
     "data exfiltration attempt"),
    (r"(unlock|open)\s+(all|every)\b.*(door|lock)", "unlock all locks"),
    (r"turn\s+off\s+(all\s+)?(the\s+)?(alarm|alarms|security)", "disable security devices"),
    (r"system\s+prompt", "system prompt probing"),
]

# Weaker signals: not conclusive, escalate to the LLM tier.
_SUSPICIOUS_PATTERNS: list[str] = [
    r"\bignore\b",
    r"\binstead\b",
    r"\boverride\b",
    r"\bbypass\b",
    r"\bactually\b",
    r"\beverything\b",
]


class RuleFilter:
    """Pattern-based first tier of the prompt injection detector."""

    def __init__(self) -> None:
        self._strong = [(re.compile(p, re.IGNORECASE), label) for p, label in _STRONG_PATTERNS]
        self._suspicious = [re.compile(p, re.IGNORECASE) for p in _SUSPICIOUS_PATTERNS]

    def inspect(self, text: str) -> RuleResult:
        text = text or ""
        for pattern, label in self._strong:
            if pattern.search(text):
                return RuleResult(Signal.MALICIOUS, label)
        for pattern in self._suspicious:
            if pattern.search(text):
                return RuleResult(Signal.UNCERTAIN, "suspicious tokens, needs further check")
        return RuleResult(Signal.BENIGN, "no injection signal")
