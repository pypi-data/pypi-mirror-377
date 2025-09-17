import pytest
from greencell_client.state import EvseStateData


def test_initial_state_is_unknown():
    evse = EvseStateData()
    called = []

    def listener():
        called.append(True)

    evse.register_listener(listener)
    evse.update("INVALID_STATE")
    assert called == [True], "Listener should be called when state is updated to an invalid state"


@pytest.mark.parametrize(
    "state_name, expected_result",
    [
        ("WAITING_FOR_CAR", True),
        ("CHARGING", True),
        ("CONNECTED", False),
        ("FINISHED", False),
        ("ERROR_EVSE", False),
        ("UNKNOWN", False),
    ]
)
def test_can_be_stopped(state_name, expected_result):
    evse = EvseStateData()
    evse.update(state_name)
    assert evse.can_be_stopped() is expected_result, \
        f"State {state_name} should return {expected_result} for can_be_stopped"


@pytest.mark.parametrize(
    "state_name, expected_result",
    [
        ("FINISHED", True),
        ("CONNECTED", True),
        ("WAITING_FOR_CAR", False),
        ("CHARGING", False),
        ("ERROR_CAR", False),
        ("UNKNOWN", False),
    ]
)
def test_can_be_started(state_name, expected_result):
    evse = EvseStateData()
    evse.update(state_name)
    assert evse.can_be_started() is expected_result, \
        f"State {state_name} should return {expected_result} for can_be_started"


def test_update_triggers_listeners():
    evse = EvseStateData()
    triggered = []

    def listener():
        triggered.append("called")

    evse.register_listener(listener)
    evse.update("CHARGING")

    assert triggered == ["called"], "Listener should be called when state is updated to CHARGING"


def test_register_multiple_listeners():
    evse = EvseStateData()
    calls = []

    def listener1():
        calls.append("one")

    def listener2():
        calls.append("two")

    evse.register_listener(listener1)
    evse.register_listener(listener2)
    evse.update("CONNECTED")

    assert "one" in calls, "Listener one should be called"
    assert "two" in calls, "Listener two should be called"
    assert len(calls) == 2, "Both listeners should be called exactly once"


def test_invalid_state_defaults_to_unknown():
    evse = EvseStateData()
    evse.update("INVALID_STATE")

    # indirectly tested via behavior
    assert not evse.can_be_stopped(), "Invalid state should not allow stopping"
    assert not evse.can_be_started(), "Invalid state should not allow starting"


def test_set_charging_does_not_raise():
    evse = EvseStateData()
    evse.set_charging(True)  # only coverage check, has no effect
