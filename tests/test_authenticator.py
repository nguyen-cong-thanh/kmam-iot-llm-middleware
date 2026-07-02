"""Tests for the Authenticator (FR1)."""

from kmam.authentication import Authenticator
from kmam.context import RequestContext


def test_valid_token_resolves_identity():
    auth = Authenticator.from_config()
    identity = auth.authenticate("token-operator-001")
    assert identity is not None
    assert identity.user_id == "bob"
    assert identity.role == "operator"


def test_invalid_token_returns_none():
    auth = Authenticator.from_config()
    assert auth.authenticate("token-unknown") is None
    assert auth.authenticate(None) is None
    assert auth.authenticate("") is None


def test_enrich_populates_context():
    auth = Authenticator.from_config()
    ctx = RequestContext(session_id="token-admin-001")
    decision = auth.enrich(ctx)
    assert decision.allowed
    assert ctx.user_id == "alice"
    assert ctx.role == "admin"
    assert ctx.attributes["department"] == "it"


def test_enrich_denies_invalid_credential():
    auth = Authenticator.from_config()
    ctx = RequestContext(session_id="forged-token")
    decision = auth.enrich(ctx)
    assert not decision.allowed
    assert ctx.role is None


def test_enrich_keeps_request_attributes():
    auth = Authenticator.from_config()
    ctx = RequestContext(session_id="token-operator-001", attributes={"time": "09:00"})
    auth.enrich(ctx)
    assert ctx.attributes["time"] == "09:00"
    assert ctx.attributes["department"] == "facilities"
