from greencell_client.utils import GreencellUtils


def test_device_is_habu_den():
    assert GreencellUtils.device_is_habu_den("EVGC021B22752405ZM0018"), \
        "Should return True for Habu Den serial prefix"
    assert not GreencellUtils.device_is_habu_den("EVGC031B22752405ZM0018"), \
        "Should return False for non-Habu Den serial prefix"
    assert not GreencellUtils.device_is_habu_den("EVGC022B22752405ZM0018"), \
        "Should return True for exact Habu Den serial prefix match"
    assert not GreencellUtils.device_is_habu_den("HABU_DEN"), \
        "Should return False for completely different serial"
