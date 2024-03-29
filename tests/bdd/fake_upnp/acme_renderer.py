from .fake_upnp_device import FakeDeviceDescriptor, FakeAsyncUpnpDevice
from .av_transport import FakeAVTransportService
from .rendering_control import FakeRenderingControlService
from .connection_manager import FakeConnectionManagerService

_descriptor = FakeDeviceDescriptor(name="AcmeRenderer",
                                   friendly_name="Acme Super Blast Renderer",
                                   location='http://192.168.99.1:5000',
                                   udn='13bf6358-00b8-101b-8000-74dfbfed7306',
                                   device_type='MediaRenderer',
                                   service_types=['RenderingControl:1', 'ConnectionManager:1', 'AVTransport:1'])


def factory():
    device = FakeAsyncUpnpDevice(_descriptor)
    device.mock_add_service(FakeConnectionManagerService(device))
    device.mock_add_service(FakeAVTransportService(device))
    device.mock_add_service(FakeRenderingControlService(device))
    return device
