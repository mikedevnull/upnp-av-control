from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from .fake_upnp import create_fake_device
from .async_utils import sync
import asyncio
import logging

_logger = logging.getLogger(__name__)

scenarios('discovery.feature')


@given('a client listens for discovery events')
@sync
async def discovery_events_subscribed(event_bus_connection):
    result = await event_bus_connection.send(method='subscribe', params={'category': 'discovery'})
    assert result is True


@when(parsers.parse('a {device_type} {name} {action} the network'))
def device_appears_or_leaves(test_context, name, action):
    assert action in ('appears on', 'leaves')
    if action == 'appears on':
        descriptor = create_fake_device(name)
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
async def check_device_notification(test_context, event_bus_connection, action, name):
    action_to_methods = {'new': 'new_device', 'lost': 'device_lost'}
    assert action in action_to_methods
    descriptor = create_fake_device(name)
    event = await event_bus_connection.wait_for_notification()
    assert event.params['udn'] == descriptor.udn
    assert event.method == action_to_methods.get(action)


@then(parsers.cfparse('the media server {name} will be in the library API device list'))
@sync
async def check_server_in_devicelist(test_context, webclient, name):
    response = await webclient.get('/library/devices')
    assert response.status_code == 200
    descriptor = test_context.get_device(name)
    expected_entry = {'friendly_name': descriptor.friendly_name, 'udn': descriptor.udn}
    assert expected_entry in response.json()


@then(parsers.cfparse('the media server {name} will not be in the library API device list'))
@sync
async def check_server_not_in_devicelist(test_context, webclient, name):
    response = await webclient.get('/library/devices')
    assert response.status_code == 200
    device = create_fake_device(name)
    expected_entry = {'friendly_name': device.friendly_name, 'udn': device.udn}
    assert expected_entry not in response.json()


@then(parsers.cfparse('the media renderer {name} will be in the player API device list'))
@sync
async def check_renderer_in_devicelist(test_context, webclient, name):
    response = await webclient.get('/player/devices')
    assert response.status_code == 200
    descriptor = test_context.get_device(name)
    expected_entry = {'name': descriptor.friendly_name, 'udn': descriptor.udn}
    assert expected_entry in response.json()['data']


@then('the client will receive no notification')
@sync
async def check_no_device_notification(event_bus_connection):
    event_bus_connection.timeout = 1
    with pytest.raises(asyncio.TimeoutError):
        await event_bus_connection.wait_for_notification()
