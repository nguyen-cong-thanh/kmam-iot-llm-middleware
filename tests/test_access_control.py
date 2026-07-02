"""Tests for the AccessControlEngine (FR2): RBAC base + ABAC conditions."""

from kmam.access_control import AccessControlEngine
from kmam.context import RequestContext


def _ctx(role, device_id, action, attributes=None):
    return RequestContext(
        session_id="s1",
        user_id="u1",
        role=role,
        device_id=device_id,
        action=action,
        attributes=attributes or {},
    )


def _engine():
    return AccessControlEngine.from_config()


def test_admin_allowed_everywhere():
    assert _engine().authorize(_ctx("admin", "lock_front", "unlock")).allowed


def test_operator_allowed_on_lights():
    assert _engine().authorize(_ctx("operator", "light_living", "turn_on")).allowed


def test_operator_denied_on_locks():
    d = _engine().authorize(_ctx("operator", "lock_front", "unlock"))
    assert not d.allowed
    assert "no permission" in d.reason


def test_guest_denied_brightness():
    # guest may only turn lights on/off, not set brightness.
    assert not _engine().authorize(_ctx("guest", "light_living", "set_brightness")).allowed


def test_guest_allowed_turn_on():
    assert _engine().authorize(_ctx("guest", "light_living", "turn_on")).allowed


def test_unknown_role_denied():
    assert not _engine().authorize(_ctx("intruder", "light_living", "turn_on")).allowed


def test_unknown_device_denied():
    assert not _engine().authorize(_ctx("admin", "ghost", "unlock")).allowed


def test_abac_condition_within_time_window():
    # operator may set temperature only between 06:00 and 22:00.
    d = _engine().authorize(
        _ctx("operator", "ac_bedroom", "set_temperature", {"time": "12:00"})
    )
    assert d.allowed


def test_abac_condition_outside_time_window_denied():
    d = _engine().authorize(
        _ctx("operator", "ac_bedroom", "set_temperature", {"time": "23:30"})
    )
    assert not d.allowed
    assert "condition" in d.reason


def test_environment_overrides_attributes():
    engine = _engine()
    ctx = _ctx("operator", "ac_bedroom", "set_temperature", {"time": "23:30"})
    # An explicit environment can supply the evaluation-time attributes.
    assert engine.authorize(ctx, environment={"time": "09:00"}).allowed
