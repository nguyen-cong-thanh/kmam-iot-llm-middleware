"""Authenticator (FR1): establish the identity behind a request at the middleware.

The credential of a session (a token issued by the system) is verified here and mapped
to a known user identity with its role and attributes. The identity used for
authorization is therefore established independently of anything the agent claims in
its output (report section 3.2.1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from kmam.context import Decision, RequestContext

STAGE = "authentication"


@dataclass(frozen=True)
class Identity:
    """An authenticated user identity bound to a session."""

    user_id: str
    role: str
    attributes: dict[str, Any] = field(default_factory=dict)


class Authenticator:
    """Verifies a session credential and resolves it to an :class:`Identity`."""

    def __init__(self, sessions: dict[str, Identity]) -> None:
        self.sessions = sessions

    @classmethod
    def from_config(cls, identities_path: str | Path | None = None) -> "Authenticator":
        if identities_path is None:
            text = (resources.files("kmam") / "config" / "identities.yaml").read_text(
                encoding="utf-8"
            )
        else:
            text = Path(identities_path).read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        sessions = {
            token: Identity(
                user_id=info["user_id"],
                role=info["role"],
                attributes=info.get("attributes") or {},
            )
            for token, info in (data.get("sessions") or {}).items()
        }
        return cls(sessions)

    def authenticate(self, token: str | None) -> Identity | None:
        """Return the identity bound to ``token`` or ``None`` if it is not valid."""
        if not token:
            return None
        return self.sessions.get(token)

    def enrich(self, ctx: RequestContext) -> Decision:
        """Verify ``ctx.session_id`` as a credential and fill identity fields.

        On success the context's ``user_id``, ``role`` and ``attributes`` are populated
        and an allow decision is returned. Otherwise the context is left unchanged and a
        deny decision is returned, per the default-deny principle.
        """
        identity = self.authenticate(ctx.session_id)
        if identity is None:
            return Decision.deny(STAGE, "invalid or missing session credential")
        ctx.user_id = identity.user_id
        ctx.role = identity.role
        ctx.attributes = {**identity.attributes, **ctx.attributes}
        return Decision.allow(STAGE, f"authenticated as {identity.user_id}")
