from .fake_upnp_device import FakeDeviceDescriptor, FakeAsyncUpnpDevice
from .av_transport import FakeAVTransportService
from .rendering_control import FakeRenderingControlService
from .connection_manager import FakeConnectionManagerService

_descriptor = FakeDeviceDescriptor(name="PhonoRenderer",
                                   friendly_name="Phono foo",
                                   location='http://192.168.99.82:5000',
                                   udn='c8057822-7c69-42aa-9dbc-091a81adc529',
                                   device_type='MediaRenderer',
                                   service_types=['RenderingControl:1', 'ConnectionManager:1', 'AVTransport:1'])


def factory():
    device = FakeAsyncUpnpDevice(_descriptor)
    device.mock_add_service(FakeConnectionManagerService(device))
    device.mock_add_service(FakeAVTransportService(device))
    device.mock_add_service(FakeRenderingControlService(device))
    return device
