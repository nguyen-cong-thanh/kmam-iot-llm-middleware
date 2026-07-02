"""CommandValidator (FR3): validate a control command before it reaches a device.

Validation is whitelist based (report section 3.2.3): the action must be declared for
the device type and every parameter must match its :class:`ParamSpec` (type and safe
range). Anything not explicitly allowed is rejected, in line with the default-deny
principle.
"""

from __future__ import annotations

from pathlib import Path

from kmam.context import Decision, RequestContext
from kmam.devices.models import DeviceCatalog, UnknownDeviceError

STAGE = "command_validation"


class CommandValidator:
    """Checks that a command's action and parameters are valid for the target device."""

    def __init__(self, catalog: DeviceCatalog) -> None:
        self.catalog = catalog

    @classmethod
    def from_config(cls, devices_path: str | Path | None = None) -> "CommandValidator":
        return cls(DeviceCatalog.load(devices_path))

    def validate(self, ctx: RequestContext) -> Decision:
        if not ctx.action:
            return Decision.deny(STAGE, "no action specified")

        try:
            device = self.catalog.get_device(ctx.device_id)
        except UnknownDeviceError:
            return Decision.deny(STAGE, f"unknown device: {ctx.device_id}")

        device_type = self.catalog.get_type(device.type)
        if not device_type.has_action(ctx.action):
            return Decision.deny(
                STAGE, f"action '{ctx.action}' is not allowed for device type '{device.type}'"
            )

        action_spec = device_type.get_action(ctx.action)
        params = ctx.params or {}

        unexpected = set(params) - set(action_spec.params)
        if unexpected:
            return Decision.deny(STAGE, f"unexpected parameter(s): {sorted(unexpected)}")

        for name, spec in action_spec.params.items():
            if name not in params:
                return Decision.deny(STAGE, f"missing parameter: {name}")
            if not spec.is_valid(params[name]):
                return Decision.deny(
                    STAGE,
                    f"parameter '{name}'={params[name]!r} is out of safe range or wrong type",
                )

        return Decision.allow(STAGE, "command valid")
