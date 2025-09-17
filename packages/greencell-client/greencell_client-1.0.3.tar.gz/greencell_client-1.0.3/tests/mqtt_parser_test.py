from greencell_client import mqtt_parser
from greencell_client.elec_data import ElecData3Phase, ElecDataSinglePhase


def test_parse_3phase_msg():
    msg = '{"l1": 230.0, "l2": 230.0, "l3": 230.0}'
    elec_data = ElecData3Phase()

    assert mqtt_parser.MqttParser.parse_3phase_msg(msg, elec_data)
    assert elec_data.l1 == 230.0, "3-phase data should be updated correctly for l1"
    assert elec_data.l2 == 230.0, "3-phase data should be updated correctly for l2"
    assert elec_data.l3 == 230.0, "3-phase data should be updated correctly for l3"


def test_parse_3phase_msg_invalid_json():
    msg = '{"l1": 230.0, "l2": 230.0, "l3": 230.0'  # Missing closing brace
    elec_data = ElecData3Phase()

    assert not mqtt_parser.MqttParser.parse_3phase_msg(msg, elec_data)
    assert elec_data.l1 is None, "3-phase data should remain None on invalid JSON"
    assert elec_data.l2 is None, "3-phase data should remain None on invalid JSON"
    assert elec_data.l3 is None, "3-phase data should remain None on invalid JSON"


def test_parse_3phase_msg_key_error():
    msg = '{"l1": 230.0, "l2": 230.0}'  # Missing l3 key
    elec_data = ElecData3Phase()

    assert mqtt_parser.MqttParser.parse_3phase_msg(msg, elec_data)
    assert elec_data.l1 == 230.0, "3-phase data should be updated correctly for l1"
    assert elec_data.l2 == 230.0, "3-phase data should be updated correctly for l2"
    assert elec_data.l3 is None, "3-phase data should remain None for missing l3 key"


def test_parse_3phase_msg_type_error():
    msg = '{"l1": "not_a_float", "l2": 230.0, "l3": 230.0}'
    elec_data = ElecData3Phase()

    assert mqtt_parser.MqttParser.parse_3phase_msg(msg, elec_data)
    assert elec_data.l1 == "not_a_float", \
        "3-phase data should accept string input without conversion"
    assert elec_data.l2 == 230.0, "3-phase data should be updated correctly for l2"
    assert elec_data.l3 == 230.0, "3-phase data should be updated correctly for l3"


def test_parse_single_phase_msg():
    msg = '{"voltage": 230.0}'
    elec_data = ElecDataSinglePhase()

    assert mqtt_parser.MqttParser.parse_single_phase_msg(msg, "voltage", elec_data)
    assert elec_data.data == 230.0, "Single phase data should be updated correctly"


def test_parse_single_phase_msg_invalid_key():
    msg = '{"voltage": 230.0}'
    elec_data = ElecDataSinglePhase()

    assert not mqtt_parser.MqttParser.parse_single_phase_msg(msg, "current", elec_data)
    assert elec_data.data is None, "Single phase data should remain None for invalid key"


def test_parse_single_phase_msg_invalid_json():
    msg = '{"voltage": 230.0'
    elec_data = ElecDataSinglePhase()

    assert not mqtt_parser.MqttParser.parse_single_phase_msg(msg, "voltage", elec_data)
    assert elec_data.data is None, "Single phase data should remain None on invalid JSON"


def test_parse_single_phase_msg_type_error():
    msg = '{"voltage": "not_a_float"}'
    elec_data = ElecDataSinglePhase()

    assert mqtt_parser.MqttParser.parse_single_phase_msg(msg, "voltage", elec_data)
    assert elec_data.data == "not_a_float", \
        "Single phase data should accept string input without conversion"
