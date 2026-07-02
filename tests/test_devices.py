"""Tests for the device catalog and simulator."""

import pytest

from kmam.devices import (
    DeviceCatalog,
    DeviceSimulator,
    ParamSpec,
    UnknownActionError,
    UnknownDeviceError,
)


def test_catalog_loads_default_config():
    catalog = DeviceCatalog.load()
    assert "thermostat" in catalog.device_types
    assert "lock_front" in catalog.devices
    thermostat = catalog.get_type("thermostat")
    assert thermostat.has_action("set_temperature")
    celsius = thermostat.get_action("set_temperature").params["celsius"]
    assert celsius.min == 16 and celsius.max == 30


def test_param_spec_validation():
    spec = ParamSpec(name="celsius", type="int", min=16, max=30)
    assert spec.is_valid(20) is True
    assert spec.is_valid(15) is False
    assert spec.is_valid(31) is False
    assert spec.is_valid(20.5) is False  # wrong type
    assert spec.is_valid(True) is False  # bool is not a valid int


def test_simulator_executes_and_updates_state():
    sim = DeviceSimulator.from_config()
    result = sim.execute("lock_front", "unlock")
    assert result.success is True
    assert result.state["locked"] is False
    assert sim.get_device("lock_front").state["last_action"] == "unlock"


def test_simulator_applies_params():
    sim = DeviceSimulator.from_config()
    result = sim.execute("ac_bedroom", "set_temperature", {"celsius": 24})
    assert result.state["celsius"] == 24


def test_simulator_executes_unsafe_value_without_middleware():
    # The bare simulator does not enforce safe ranges (baseline KB7 behaviour).
    sim = DeviceSimulator.from_config()
    result = sim.execute("ac_bedroom", "set_temperature", {"celsius": 99})
    assert result.state["celsius"] == 99


def test_simulator_unknown_device():
    sim = DeviceSimulator.from_config()
    with pytest.raises(UnknownDeviceError):
        sim.execute("does_not_exist", "unlock")


def test_simulator_unknown_action():
    sim = DeviceSimulator.from_config()
    with pytest.raises(UnknownActionError):
        sim.execute("lock_front", "explode")


def test_reset_clears_state():
    sim = DeviceSimulator.from_config()
    sim.execute("light_living", "turn_on")
    assert sim.get_device("light_living").state
    sim.reset()
    assert sim.get_device("light_living").state == {}
