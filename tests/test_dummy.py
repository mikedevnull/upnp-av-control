import upnpavcontrol


def test_magic_number():
    assert upnpavcontrol.generate_useless_magic_number() == 42
