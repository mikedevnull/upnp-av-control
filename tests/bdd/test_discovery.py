from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from functools import wraps
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


scenarios('discovery.feature')


@given('a client listens for discovery events')
@sync
async def discovery_events_subscribed(event_bus_connection):
    result = await event_bus_connection.send(method='subscribe', params={'category': 'discovery'})
    assert result is True


@given(parsers.parse('a device {name} already present on the network'))
def a_device_foomediaserver_already_present_on_the_network(test_context, name):
    device = fake_devices.get_device(name)
    test_context.add_device_to_network(name, device, notify=True)


@when(parsers.parse('a {device_type} {name} {action} the network'))
def device_appears_or_leaves(test_context, name, action):
    assert action in ('appears on', 'leaves')
    if action == 'appears on':
        descriptor = fake_devices.get_device(name)
        test_context.add_device_to_network(name, descriptor, notify=True)
    else:
        test_context.remove_device_to_network(name, notify=True)


@when('the client unsubscribes for discovery events')
@sync
async def unsubscribe_discovery_events(event_bus_connection):
    result = await event_bus_connection.send(method='unsubscribe', params={'category': 'discovery'})
    assert result is True


@then(parsers.cfparse('the client will be notified about the {action} {name}'))
@sync
async def check_device_notification(event_bus_connection, action, name):
    action_to_methods = {'new': 'new_device', 'lost': 'device_lost'}
    assert action in action_to_methods
    descriptor = fake_devices.get_device(name)
    event = await event_bus_connection.wait_for_notification()
    assert event.params['udn'] == descriptor.udn
    assert event.method == action_to_methods.get(action)


@then(parsers.cfparse('the media server {name} will be in the library API device list'))
@sync
async def check_server_in_devicelist(webclient, name):
    response = await webclient.get('/library/devices')
    assert response.status_code == 200
    descriptor = fake_devices.get_device(name)
    expected_entry = {'friendly_name': descriptor.friendly_name, 'udn': descriptor.udn}
    assert expected_entry in response.json()


@then(parsers.cfparse('the media server {name} will not be in the library API device list'))
@sync
async def check_server_not_in_devicelist(webclient, name):
    response = await webclient.get('/library/devices')
    assert response.status_code == 200
    descriptor = fake_devices.get_device(name)
    expected_entry = {'friendly_name': descriptor.friendly_name, 'udn': descriptor.udn}
    assert expected_entry not in response.json()


@then(parsers.cfparse('the media renderer {name} will be in the player API device list'))
@sync
async def check_renderer_in_devicelist(webclient, name):
    response = await webclient.get('/player/devices')
    assert response.status_code == 200
    descriptor = fake_devices.get_device(name)
    expected_entry = {'name': descriptor.friendly_name, 'udn': descriptor.udn}
    assert expected_entry in response.json()['data']


@then('the client will receive no notification')
@sync
async def check_no_device_notification(event_bus_connection):
    event_bus_connection.timeout = 1
    with pytest.raises(asyncio.TimeoutError):
        await event_bus_connection.wait_for_notification()
