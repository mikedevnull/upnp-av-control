from .fake_upnp_device import FakeDeviceDescriptor, FakeAsyncUpnpDevice

_descriptor = FakeDeviceDescriptor(name='BazPrinter',
                                   friendly_name="Baz inc printer",
                                   location='http://192.168.99.55',
                                   udn='1234-5667-999-0',
                                   device_type='Printer',
                                   service_types=[])


def factory():
    device = FakeAsyncUpnpDevice(_descriptor)
    return device