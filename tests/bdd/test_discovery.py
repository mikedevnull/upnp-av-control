from pytest_bdd import scenario, given, when, then
from functools import wraps
from ..unit import advertisement_data
from . import fake_devices
import asyncio
import logging

_logger = logging.getLogger(__name__)


def sync(func):
    @wraps(func)
    def synced_func(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return synced_func


@scenario('discovery.feature', 'New MediaServer advertised')
def test_media_server_discovered():
    pass


@given('a client listens for discovery events')
@sync
async def event_bus(event_bus_connection):
    result = await event_bus_connection.send(method='subscribe', params={'category': 'discovery'})
    assert result is True


@when('a MediaServer appears on the network')
def device_appears(test_context):
    name = 'FooServer'
    device = fake_devices.get_device(name)
    test_context.add_device_to_network(name, device, notify=True)


@then('the client will receive a notification')
@sync
async def check_new_device_notification(event_bus_connection):
    name = 'FooServer'
    descriptor = fake_devices.get_device(name)
    event = await event_bus_connection.wait_for_notification()
    assert event.params['udn'] == descriptor.udn
