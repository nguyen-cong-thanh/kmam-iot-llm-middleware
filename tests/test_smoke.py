"""Smoke test: the package imports and shared types behave as expected."""

from kmam import __version__
from kmam.context import Decision, RequestContext, Verdict


def test_package_imports():
    assert __version__


def test_decision_helpers():
    allow = Decision.allow(stage="test", reason="ok")
    deny = Decision.deny(stage="test", reason="blocked")
    assert allow.allowed is True
    assert deny.allowed is False
    assert allow.verdict is Verdict.ALLOW
    assert deny.verdict is Verdict.DENY


def test_request_context_defaults():
    ctx = RequestContext(session_id="s1")
    assert ctx.attributes == {}
    assert ctx.params == {}
    assert ctx.raw_user_request == ""
