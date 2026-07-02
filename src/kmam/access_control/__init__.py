"""Access control (FR2): RBAC base combined with ABAC conditions, policy-driven."""

from kmam.access_control.engine import AccessControlEngine
from kmam.access_control.policy import AllowRule, Condition, Policy

__all__ = ["AccessControlEngine", "AllowRule", "Condition", "Policy"]
