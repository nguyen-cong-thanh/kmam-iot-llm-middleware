"""Software simulation of IoT devices.

The simulator stands in for real hardware (report section 3.1.2). It executes whatever
command it is handed and updates device state accordingly. It deliberately does NOT
enforce permissions or safe ranges: that is the middleware's job. This separation is
what makes the "no middleware" baseline (scenario KB7) meaningful, since an unsafe
command reaches the device and takes effect when the middleware is absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kmam.devices.models import (
    Device,
    DeviceCatalog,
    UnknownActionError,
)

# Convenience semantic flags applied on top of the generic state update, so tests and
# scenarios can assert on a device's status in a readable way.
_BOOL_EFFECTS = {
    "lock": ("locked", True),
    "unlock": ("locked", False),
    "turn_on": ("on", True),
    "turn_off": ("on", False),
}


@dataclass
class ActionResult:
    """Outcome of executing a command on the simulator."""

    success: bool
    device_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)


class DeviceSimulator:
    """Holds device instances and executes control commands against them."""

    def __init__(self, catalog: DeviceCatalog) -> None:
        self.catalog = catalog

    @classmethod
    def from_config(cls, devices_path: str | Path | None = None) -> "DeviceSimulator":
        return cls(DeviceCatalog.load(devices_path))

    @property
    def devices(self) -> dict[str, Device]:
        return self.catalog.devices

    def get_device(self, device_id: str) -> Device:
        return self.catalog.get_device(device_id)

    def reset(self) -> None:
        """Clear the runtime state of every device."""
        for device in self.catalog.devices.values():
            device.state = {}

    def execute(
        self, device_id: str, action: str, params: dict[str, Any] | None = None
    ) -> ActionResult:
        """Execute ``action`` on ``device_id``, updating and returning its state.

        Raises :class:`UnknownDeviceError` for an unknown device and
        :class:`UnknownActionError` for an action the device type cannot perform.
        """
        params = params or {}
        device = self.catalog.get_device(device_id)
        device_type = self.catalog.get_type(device.type)
        if not device_type.has_action(action):
            raise UnknownActionError(f"{device.type} cannot perform action: {action}")

        device.state["last_action"] = action
        device.state.update(params)
        if action in _BOOL_EFFECTS:
            key, value = _BOOL_EFFECTS[action]
            device.state[key] = value

        return ActionResult(
            success=True,
            device_id=device_id,
            action=action,
            params=dict(params),
            state=dict(device.state),
        )
