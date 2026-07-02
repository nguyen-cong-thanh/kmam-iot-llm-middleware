"""AccessControlEngine (FR2): authorize a control request per command.

The engine resolves the target device's group from the device catalog, then evaluates
the policy under the default-deny principle: a request is permitted only when the
subject's role has a matching allow rule and every applicable ABAC condition holds.
Re-checking on every command (rather than trusting the agent's aggregate rights) is
what neutralizes the confused-deputy / privilege-escalation risk of report section
1.3.3.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kmam.access_control.policy import Policy
from kmam.context import Decision, RequestContext
from kmam.devices.models import DeviceCatalog, UnknownDeviceError

STAGE = "access_control"


class AccessControlEngine:
    """Evaluates whether a subject may perform an action on a device."""

    def __init__(self, policy: Policy, catalog: DeviceCatalog) -> None:
        self.policy = policy
        self.catalog = catalog

    @classmethod
    def from_config(
        cls,
        policies_path: str | Path | None = None,
        devices_path: str | Path | None = None,
    ) -> "AccessControlEngine":
        return cls(Policy.load(policies_path), DeviceCatalog.load(devices_path))

    def authorize(
        self, ctx: RequestContext, environment: dict[str, Any] | None = None
    ) -> Decision:
        if not ctx.role:
            return Decision.deny(STAGE, "request has no authenticated role")
        if not ctx.action:
            return Decision.deny(STAGE, "no action specified")
        if not self.policy.has_role(ctx.role):
            return Decision.deny(STAGE, f"unknown role: {ctx.role}")

        try:
            device = self.catalog.get_device(ctx.device_id)
        except UnknownDeviceError:
            return Decision.deny(STAGE, f"unknown device: {ctx.device_id}")

        group = device.group
        rules = self.policy.roles[ctx.role]
        if not any(rule.matches(group, ctx.action) for rule in rules):
            return Decision.deny(
                STAGE,
                f"role '{ctx.role}' has no permission for '{ctx.action}' on group '{group}'",
            )

        attributes = {**ctx.attributes, **(environment or {})}
        for condition in self.policy.conditions:
            if condition.applies_to(ctx.role, group, ctx.action) and not condition.is_satisfied(
                attributes
            ):
                return Decision.deny(
                    STAGE, f"context condition not satisfied: {condition.require}"
                )

        return Decision.allow(STAGE, "authorized")
