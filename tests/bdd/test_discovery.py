from pytest_bdd import scenarios, given, when, then, parsers
from .fake_upnp import create_fake_device
from .async_utils import sync
import logging
from .common_steps import *  # noqa: F403, F401

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


@when('the client unsubscribes from discovery events')
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
    response = await webclient.get('/api/library/')
    assert response.status_code == 200
    descriptor = test_context.get_device(name)
    for entry in response.json()['data']:
        if entry['id'] == descriptor.udn:
            server = entry
            break
    assert server is not None
    assert server['attributes']['name'] == descriptor.friendly_name


@then(parsers.cfparse('the media server {name} will not be in the library API device list'))
@sync
async def check_server_not_in_devicelist(test_context, webclient, name):
    response = await webclient.get('/api/library/')
    assert response.status_code == 200
    device = create_fake_device(name)
    parsed_response = response.json()['data']
    for entry in parsed_response:
        assert entry['id'] != device.udn


@then(parsers.cfparse('the media renderer {name} will be in the player API device list'))
@sync
async def check_renderer_in_devicelist(test_context, webclient, name):
    response = await webclient.get('/api/player/')
    assert response.status_code == 200
    descriptor = test_context.get_device(name)
    renderer = None
    for entry in response.json()['data']:
        if entry['id'] == descriptor.udn:
            renderer = entry
            break
    assert renderer is not None
    assert renderer['attributes']['name'] == descriptor.friendly_name
