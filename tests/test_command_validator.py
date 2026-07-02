"""Tests for the CommandValidator (FR3)."""

from kmam.context import RequestContext
from kmam.validation import CommandValidator


def _ctx(device_id, action, params=None):
    return RequestContext(session_id="s1", device_id=device_id, action=action, params=params or {})


def test_valid_command_allowed():
    v = CommandValidator.from_config()
    assert v.validate(_ctx("ac_bedroom", "set_temperature", {"celsius": 24})).allowed


def test_parameterless_action_allowed():
    v = CommandValidator.from_config()
    assert v.validate(_ctx("lock_front", "unlock")).allowed


def test_action_not_in_whitelist_denied():
    v = CommandValidator.from_config()
    d = v.validate(_ctx("lock_front", "explode"))
    assert not d.allowed
    assert "not allowed" in d.reason


def test_param_out_of_safe_range_denied():
    v = CommandValidator.from_config()
    d = v.validate(_ctx("ac_bedroom", "set_temperature", {"celsius": 99}))
    assert not d.allowed
    assert "safe range" in d.reason


def test_unknown_device_denied():
    v = CommandValidator.from_config()
    assert not v.validate(_ctx("ghost_device", "unlock")).allowed


def test_missing_param_denied():
    v = CommandValidator.from_config()
    d = v.validate(_ctx("light_living", "set_brightness"))
    assert not d.allowed
    assert "missing parameter" in d.reason


def test_unexpected_param_denied():
    v = CommandValidator.from_config()
    d = v.validate(_ctx("lock_front", "unlock", {"force": True}))
    assert not d.allowed
    assert "unexpected" in d.reason


def test_no_action_denied():
    v = CommandValidator.from_config()
    assert not v.validate(_ctx("lock_front", None)).allowed


def test_wrong_param_type_denied():
    v = CommandValidator.from_config()
    d = v.validate(_ctx("light_living", "set_brightness", {"level": "high"}))
    assert not d.allowed
