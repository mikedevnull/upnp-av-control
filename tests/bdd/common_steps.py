from pytest_bdd import scenarios, given, when, then, parsers
from .async_utils import sync
from .fake_upnp import create_fake_device


@given(parsers.parse('a device {name} already present on the network'))
def a_device_foomediaserver_already_present_on_the_network(test_context, name):
    device = create_fake_device(name)
    test_context.add_device_to_network(name, device, notify=True)


@given(parsers.parse('a client subscribed to playback notifications from {renderer_name}'))
@sync
async def discovery_events_subscribed(test_context, event_bus_connection, renderer_name):
    descriptor = test_context.get_device(renderer_name)
    result = await event_bus_connection.send(method='subscribe',
                                             params={
                                                 'category': 'playbackinfo',
                                                 'udn': descriptor.udn
                                             })
    assert result is True
