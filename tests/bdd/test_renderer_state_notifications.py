from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from .async_utils import sync
from functools import wraps
import asyncio
import logging

_logger = logging.getLogger(__name__)

scenarios('renderer_state_notifications.feature')


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


@when(parsers.cfparse('the playback volume of AcmeRenderer changes to {volume:d}'))
@sync
async def unsubscribe_discovery_events(test_context, event_bus_connection, volume):
    device = test_context.get_device('AcmeRenderer')
    await device.service('urn:schemas-upnp-org:service:RenderingControl:1')._set_volume(volume)


@then(parsers.cfparse('the client will be notified about the new volume {volume:d}'))
@sync
async def check_device_notification(event_bus_connection, volume):
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['volume_percent'] == volume