import UpnpAVControl


def test_magic_number():
    assert UpnpAVControl.generate_useless_magic_number() == 42
