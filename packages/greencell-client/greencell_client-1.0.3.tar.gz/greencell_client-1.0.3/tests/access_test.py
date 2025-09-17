import pytest
from unittest.mock import Mock

from greencell_client.access import GreencellAccess, GreencellHaAccessLevel

# === Initialization ===


def test_initial_access_level():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    assert not access.can_execute(), "can_execute failed when setting access level to read only"
    assert not access.is_disabled(), "is_disabled failed when setting access level to read only"

# === Access level update ===


@pytest.mark.parametrize(
    "new_level, expected_can_execute, expected_is_disabled",
    [
        ("EXECUTE", True, False),
        ("READ", False, False),
        ("DISABLED", False, True),
        ("UNAVAILABLE", False, True),
        ("INVALID_LEVEL", False, True),  # fallback to DISABLED
    ]
)
def test_update_access_level_behavior(new_level, expected_can_execute, expected_is_disabled):
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    access.update(new_level)
    assert access.can_execute() == expected_can_execute, f"can_execute failed for {new_level}"
    assert access.is_disabled() == expected_is_disabled, f"is_disabled failed for {new_level}"

# === Listener notification ===


def test_listener_is_called_on_update():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    mock_listener = Mock()
    access.register_listener(mock_listener)

    access.update("EXECUTE")

    mock_listener.assert_called_once(), "Listener was not called on access level update"


def test_multiple_listeners():
    access = GreencellAccess(GreencellHaAccessLevel.DISABLED)
    listeners = [Mock(), Mock(), Mock()]
    for listener in listeners:
        access.register_listener(listener)

    access.update("READ")

    for listener in listeners:
        listener.assert_called_once(), "Listener was not called on access level update"

# === No listeners registered ===


def test_no_listeners_registered():
    access = GreencellAccess(GreencellHaAccessLevel.OFFLINE)
    access.update("EXECUTE")
    assert access.can_execute(), \
        "Access level should change to EXECUTE when no listeners are registered"
    assert not access.is_disabled(), \
        "Access level should not change when no listeners are registered"


def test_no_listeners_after_update():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    access.update("DISABLED")
    assert access.is_disabled(), \
        "Access level should be DISABLED after update when no listeners are registered"
    assert not access.can_execute(), \
        "Access level should not be EXECUTE when no listeners are registered"

# === Access level string representation ===


def test_update_invalid_level_sets_to_disabled():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    access.update("INVALID_LEVEL")

    assert access.is_disabled(), "Access level should be DISABLED when an invalid level is provided"


def test_update_empty_string_sets_to_disabled():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    access.update("")

    assert access.is_disabled(), "Access level should be DISABLED when an empty string is provided"


def test_update_none_sets_to_disabled():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    access.update(None)
    assert access.is_disabled(), "Access level should be DISABLED when None is provided"


# === Access level from message parsing ===


def test_on_msg_updates_access_level():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    msg = '{"level": "EXECUTE"}'
    access.on_msg(msg)

    assert access.can_execute(), \
        "Access level should be EXECUTE after parsing message with EXECUTE level"
    assert not access.is_disabled(), \
        "Access level should not be DISABLED after parsing message with EXECUTE level"


def test_on_msg_invalid_json():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    msg = '{"level": "INVALID_LEVEL"'
    access.on_msg(msg)

    assert access.is_disabled(), \
        "Access level should be DISABLED after parsing invalid JSON message"
    assert not access.can_execute(), \
        "Access level should not be EXECUTE after parsing invalid JSON message"


def test_on_msg_missing_access_level():
    access = GreencellAccess(GreencellHaAccessLevel.READ)
    msg = '{"some_other_key": "value"}'
    access.on_msg(msg)

    assert access.is_disabled(), \
        "Access level should be DISABLED when access_level key is missing in message"
    assert not access.can_execute(), \
        "Access level should not be EXECUTE when access_level key is missing in message"
