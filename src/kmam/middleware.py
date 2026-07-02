"""SecurityMiddleware: the pipeline that orchestrates the five KMAM components.

A request is processed sequentially under the default-deny principle, in the order of
report Figure 3.2: authentication, prompt injection detection, authorization and command
validation. Only when every stage passes is the command forwarded to the device
simulator for execution. The decisive decision (the first deny, or the final allow) is
recorded by the audit logger.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kmam.access_control.engine import AccessControlEngine
from kmam.audit.logger import AuditLogger, AuditRecord
from kmam.authentication.authenticator import Authenticator
from kmam.context import Decision, RequestContext, Verdict
from kmam.detection.detector import PromptInjectionDetector
from kmam.devices.simulator import ActionResult, DeviceSimulator
from kmam.validation.command_validator import CommandValidator

STAGE = "middleware"


@dataclass
class MiddlewareResult:
    """Outcome of processing one control request through the pipeline."""

    decision: Decision
    executed: bool
    action_result: ActionResult | None
    record: AuditRecord

    @property
    def allowed(self) -> bool:
        return self.decision.allowed


class SecurityMiddleware:
    """Chains the KMAM components into a single access-control pipeline."""

    def __init__(
        self,
        authenticator: Authenticator,
        detector: PromptInjectionDetector,
        access_control: AccessControlEngine,
        validator: CommandValidator,
        simulator: DeviceSimulator,
        audit: AuditLogger | None = None,
    ) -> None:
        self.authenticator = authenticator
        self.detector = detector
        self.access_control = access_control
        self.validator = validator
        self.simulator = simulator
        self.audit = audit or AuditLogger()

    @classmethod
    def from_config(
        cls,
        detector: PromptInjectionDetector | None = None,
        audit_sink: str | Path | None = None,
        config_dir: str | Path | None = None,
    ) -> "SecurityMiddleware":
        """Build a middleware with components loaded from the packaged config.

        A custom ``detector`` may be supplied (for example one wired to a real LLM tier);
        otherwise a rule-only detector is used.
        """
        def _path(name: str) -> str | None:
            return str(Path(config_dir) / name) if config_dir is not None else None

        return cls(
            authenticator=Authenticator.from_config(_path("identities.yaml")),
            detector=detector or PromptInjectionDetector(),
            access_control=AccessControlEngine.from_config(
                _path("policies.yaml"), _path("devices.yaml")
            ),
            validator=CommandValidator.from_config(_path("devices.yaml")),
            simulator=DeviceSimulator.from_config(_path("devices.yaml")),
            audit=AuditLogger(sink=audit_sink),
        )

    def handle(
        self, ctx: RequestContext, environment: dict[str, Any] | None = None
    ) -> MiddlewareResult:
        """Run the request through the pipeline and execute it if fully allowed."""
        for decision in (
            lambda: self.authenticator.enrich(ctx),
            lambda: self.detector.detect(ctx),
            lambda: self.access_control.authorize(ctx, environment),
            lambda: self.validator.validate(ctx),
        ):
            result = decision()
            if not result.allowed:
                return self._finalize(ctx, result, executed=False, action_result=None)

        action_result = self.simulator.execute(ctx.device_id, ctx.action, ctx.params)
        allow = Decision(Verdict.ALLOW, "command executed", STAGE)
        return self._finalize(ctx, allow, executed=True, action_result=action_result)

    def handle_request(
        self,
        *,
        session_id: str,
        device_id: str | None = None,
        action: str | None = None,
        params: dict[str, Any] | None = None,
        raw_user_request: str = "",
        environment: dict[str, Any] | None = None,
    ) -> MiddlewareResult:
        """Convenience wrapper that builds the :class:`RequestContext` for a request."""
        ctx = RequestContext(
            session_id=session_id,
            device_id=device_id,
            action=action,
            params=params or {},
            raw_user_request=raw_user_request,
        )
        return self.handle(ctx, environment)

    def _finalize(
        self,
        ctx: RequestContext,
        decision: Decision,
        *,
        executed: bool,
        action_result: ActionResult | None,
    ) -> MiddlewareResult:
        record = self.audit.log(ctx, decision)
        return MiddlewareResult(
            decision=decision,
            executed=executed,
            action_result=action_result,
            record=record,
        )
