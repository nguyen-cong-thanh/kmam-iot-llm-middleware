"""Shared data types passed between middleware stages.

A :class:`RequestContext` is the unit of information every stage inspects, and a
:class:`Decision` is the verdict a stage (or the whole pipeline) returns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    """Outcome of a check."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass
class RequestContext:
    """A device control request after authentication has established identity.

    Fields are populated progressively: identity fields (``user_id``, ``role``,
    ``attributes``) are filled by the Authenticator, while ``device_id``,
    ``action`` and ``params`` are extracted from the agent's tool call.
    """

    session_id: str
    user_id: str | None = None
    role: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    device_id: str | None = None
    device_type: str | None = None
    action: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    raw_user_request: str = ""


@dataclass
class Decision:
    """Verdict returned by a check stage, with the reason and originating stage.

    ``tier`` is set by the prompt injection detector to record which tier settled the
    case ("rule" or "llm"), so evaluation can attribute detections per tier.
    """

    verdict: Verdict
    reason: str = ""
    stage: str = ""
    tier: str | None = None

    @property
    def allowed(self) -> bool:
        return self.verdict is Verdict.ALLOW

    @classmethod
    def allow(cls, stage: str = "", reason: str = "") -> "Decision":
        return cls(Verdict.ALLOW, reason, stage)

    @classmethod
    def deny(cls, stage: str = "", reason: str = "") -> "Decision":
        return cls(Verdict.DENY, reason, stage)
