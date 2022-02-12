from pytest_bdd import given, when, then, parsers
from .async_utils import sync
from .fake_upnp import create_fake_device
import pytest
import asyncio


@given(parsers.parse('a device {name} already present on the network'))
def a_device_foomediaserver_already_present_on_the_network(test_context, name):
    device = create_fake_device(name)
    test_context.add_device_to_network(name, device, notify=True)


async def _subscribe_to_events(renderer, event_bus_connection):
    result = await event_bus_connection.send(method='subscribe',
                                             params={
                                                 'category': 'playbackinfo',
                                                 'udn': renderer.udn
                                             })
    assert result is True


@given(parsers.parse('a client subscribed to playback notifications from {renderer_name}'))
@sync
async def playbackinfo_events_subscribed(test_context, event_bus_connection, renderer_name):
    renderer = test_context.get_device(renderer_name)
    await _subscribe_to_events(renderer, event_bus_connection)
    await event_bus_connection.clear_pending_notifications()


@when(parsers.parse('a client subscribes to playback notifications from {renderer_name}'))
@sync
async def subscribe_to_playbackinfo_events(test_context, event_bus_connection, renderer_name):
    renderer = test_context.get_device(renderer_name)
    await _subscribe_to_events(renderer, event_bus_connection)


@when(parsers.parse('the client unsubscribes from playback notifications from {renderer_name}'))
@sync
async def playbackinfo_events_unsubscribe(test_context, event_bus_connection, renderer_name):
    descriptor = test_context.get_device(renderer_name)
    result = await event_bus_connection.send(method='unsubscribe',
                                             params={
                                                 'category': 'playbackinfo',
                                                 'udn': descriptor.udn
                                             })
    assert result is True


@then('the client will receive no notification')
@sync
async def check_no_device_notification(event_bus_connection):
    event_bus_connection.timeout = 1
    with pytest.raises(asyncio.TimeoutError):
        await event_bus_connection.wait_for_notification()
