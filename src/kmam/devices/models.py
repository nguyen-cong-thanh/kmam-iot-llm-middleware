"""Device model: catalog of device types, their allowed actions and parameter specs.

Both the :class:`~kmam.devices.simulator.DeviceSimulator` and the
``CommandValidator`` (FR3) build on this catalog, so the set of allowed actions and
safe parameter ranges is declared in exactly one place (``config/devices.yaml``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


class UnknownDeviceError(KeyError):
    """Raised when a device id is not present in the catalog."""


class UnknownActionError(KeyError):
    """Raised when an action is not defined for a device type."""


@dataclass(frozen=True)
class ParamSpec:
    """Specification of a single command parameter and its safe range."""

    name: str
    type: str = "int"
    min: int | float | None = None
    max: int | float | None = None

    def is_valid(self, value: Any) -> bool:
        """Whether ``value`` matches the declared type and stays within range."""
        if self.type == "int":
            # bool is a subclass of int; reject it explicitly.
            if not isinstance(value, int) or isinstance(value, bool):
                return False
        elif self.type == "float":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
        elif self.type == "str":
            if not isinstance(value, str):
                return False
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.max:
            return False
        return True


@dataclass(frozen=True)
class ActionSpec:
    """An action a device type supports, with its parameter specifications."""

    name: str
    params: dict[str, ParamSpec] = field(default_factory=dict)


@dataclass(frozen=True)
class DeviceType:
    """A class of devices sharing the same set of actions."""

    name: str
    actions: dict[str, ActionSpec] = field(default_factory=dict)

    def has_action(self, action: str) -> bool:
        return action in self.actions

    def get_action(self, action: str) -> ActionSpec:
        try:
            return self.actions[action]
        except KeyError as exc:
            raise UnknownActionError(action) from exc


@dataclass
class Device:
    """A concrete device instance with a mutable runtime state."""

    id: str
    type: str
    group: str
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceCatalog:
    """The full set of device types and configured devices."""

    device_types: dict[str, DeviceType] = field(default_factory=dict)
    devices: dict[str, Device] = field(default_factory=dict)

    def get_type(self, name: str) -> DeviceType:
        try:
            return self.device_types[name]
        except KeyError as exc:
            raise KeyError(f"unknown device type: {name}") from exc

    def get_device(self, device_id: str) -> Device:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise UnknownDeviceError(device_id) from exc

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceCatalog":
        device_types: dict[str, DeviceType] = {}
        for type_name, type_data in (data.get("device_types") or {}).items():
            actions: dict[str, ActionSpec] = {}
            for action_name, action_data in (type_data.get("actions") or {}).items():
                params: dict[str, ParamSpec] = {}
                for param_name, param_data in ((action_data or {}).get("params") or {}).items():
                    params[param_name] = ParamSpec(name=param_name, **(param_data or {}))
                actions[action_name] = ActionSpec(name=action_name, params=params)
            device_types[type_name] = DeviceType(name=type_name, actions=actions)

        devices: dict[str, Device] = {}
        for dev in data.get("devices") or []:
            devices[dev["id"]] = Device(id=dev["id"], type=dev["type"], group=dev["group"])

        return cls(device_types=device_types, devices=devices)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "DeviceCatalog":
        """Load the catalog from ``path`` or from the packaged default config."""
        if path is None:
            text = (resources.files("kmam") / "config" / "devices.yaml").read_text(
                encoding="utf-8"
            )
        else:
            text = Path(path).read_text(encoding="utf-8")
        return cls.from_dict(yaml.safe_load(text))
