"""Policy model and evaluation for the AccessControlEngine.

The policy is expressed declaratively (``config/policies.yaml``) so that authorization
logic is separated from code, following the policy-based approach of report section
2.3.3. It combines an RBAC base (``allow`` rules per role over device groups) with
ABAC-style ``conditions`` that further constrain a decision using subject and
environment attributes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

_ANY = "*"


def _matches(pattern: str, value: str | None) -> bool:
    return pattern == _ANY or pattern == value


@dataclass(frozen=True)
class AllowRule:
    """An RBAC permission: a role may perform ``action`` on ``device_group``."""

    device_group: str = _ANY
    action: str = _ANY

    def matches(self, group: str | None, action: str | None) -> bool:
        return _matches(self.device_group, group) and _matches(self.action, action)


@dataclass(frozen=True)
class Condition:
    """An ABAC condition: when the selector matches, ``require`` must hold."""

    role: str = _ANY
    device_group: str = _ANY
    action: str = _ANY
    require: dict[str, Any] = field(default_factory=dict)

    def applies_to(self, role: str | None, group: str | None, action: str | None) -> bool:
        return (
            _matches(self.role, role)
            and _matches(self.device_group, group)
            and _matches(self.action, action)
        )

    def is_satisfied(self, attributes: dict[str, Any]) -> bool:
        for key, expected in self.require.items():
            if key == "time_between":
                now = attributes.get("time") or datetime.now().strftime("%H:%M")
                start, end = expected
                if not (start <= now <= end):
                    return False
            elif attributes.get(key) != expected:
                return False
        return True


@dataclass
class Policy:
    """Roles with their allow rules and the set of ABAC conditions."""

    roles: dict[str, list[AllowRule]] = field(default_factory=dict)
    conditions: list[Condition] = field(default_factory=list)

    def has_role(self, role: str | None) -> bool:
        return role in self.roles

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Policy":
        roles: dict[str, list[AllowRule]] = {}
        for role_name, role_data in (data.get("roles") or {}).items():
            rules = [AllowRule(**rule) for rule in (role_data or {}).get("allow", [])]
            roles[role_name] = rules

        conditions = [Condition(**cond) for cond in (data.get("conditions") or [])]
        return cls(roles=roles, conditions=conditions)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Policy":
        if path is None:
            text = (resources.files("kmam") / "config" / "policies.yaml").read_text(
                encoding="utf-8"
            )
        else:
            text = Path(path).read_text(encoding="utf-8")
        return cls.from_dict(yaml.safe_load(text))
