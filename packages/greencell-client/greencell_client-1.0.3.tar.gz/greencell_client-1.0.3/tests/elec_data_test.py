import pytest
from greencell_client.elec_data import ElecData3Phase, ElecDataSinglePhase


def test_elec_data_3phase_initial_state():
    elec = ElecData3Phase()
    assert elec.l1 is None, "Initial state for l1 should be None"
    assert elec.l2 is None, "Initial state for l2 should be None"
    assert elec.l3 is None, "Initial state for l3 should be None"


def test_elec_data_3phase_update_all_phases():
    elec = ElecData3Phase()
    elec.update_data({"l1": 10.5, "l2": 20.1, "l3": 30.0})
    assert elec.l1 == 10.5, "Phase l1 should be updated correctly"
    assert elec.l2 == 20.1, "Phase l2 should be updated correctly"
    assert elec.l3 == 30.0, "Phase l3 should be updated correctly"


def test_elec_data_3phase_partial_update():
    elec = ElecData3Phase()
    elec.update_data({"l1": 12.0})
    assert elec.l1 == 12.0, "Phase l1 should be updated correctly"
    assert elec.l2 is None, "Phase l2 should remain None when not updated"
    assert elec.l3 is None, "Phase l3 should remain None when not updated"


def test_elec_data_3phase_ignores_unknown_keys():
    elec = ElecData3Phase()
    elec.update_data({"l1": 10, "x": 999, "y": -1})
    assert elec.l1 == 10, "Phase l1 should be updated correctly"
    assert elec.l2 is None, "Phase l2 should remain None when not updated"
    assert elec.l3 is None, "Phase l3 should remain None when not updated"


def test_elec_data_single_phase_initial_state():
    elec = ElecDataSinglePhase()
    assert elec.data is None, "Initial state should be None for single phase data"


def test_elec_data_single_phase_update():
    elec = ElecDataSinglePhase()
    elec.update_data(123.45)
    assert elec.data == 123.45, "Single phase data should be updated correctly"


def test_elec_data_single_phase_update_with_string():
    elec = ElecDataSinglePhase()
    elec.update_data("not_a_float")
    assert elec.data == "not_a_float", \
        "Single phase data should accept string input without conversion"


def test_elec_data_3phase_with_none_values():
    elec = ElecData3Phase()
    elec.update_data({"l1": None, "l2": 5.5})
    assert elec.l1 is None, "Phase l1 should remain None when not updated"
    assert elec.l2 == 5.5, "Phase l2 should be updated correctly"
    assert elec.l3 is None, "Phase l3 should remain None when not updated"


def test_elec_data_3phase_invalid_phase():
    elec = ElecData3Phase()
    with pytest.raises(ValueError):
        elec.get_value("l4")  # l4 is not a valid phase


def test_elec_data_3phase_get_value():
    elec = ElecData3Phase(l1=1.0, l2=2.0, l3=3.0)
    assert elec.get_value("l1") == 1.0, "Should return value for l1"
    assert elec.get_value("l2") == 2.0, "Should return value for l2"
    assert elec.get_value("l3") == 3.0, "Should return value for l3"
