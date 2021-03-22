from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from .async_utils import sync
from functools import wraps
import asyncio
import logging

_logger = logging.getLogger(__name__)

scenarios('media_renderer_api.feature')


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
async def external_volume_change(test_context, event_bus_connection, volume):
    device = test_context.get_device('AcmeRenderer')
    await device.service('urn:schemas-upnp-org:service:RenderingControl:1')._set_volume(volume)


@when(parsers.cfparse('the client requests to change the volume of {device_name} to {volume:d}'))
@sync
async def change_renderer_volume(test_context, device_name, webclient, volume):
    if device_name == "an unkown device":
        udn = 'fake-udn-no-device-has-this'
    else:
        device = test_context.get_device(device_name)
        udn = device.udn
    test_context.last_response = await webclient.put(f'/player/{udn}/volume', json={'volume_percent': volume})


@when(parsers.cfparse('the client requests the volume of {device_name}'))
@sync
async def query_renderer_volume(test_context, device_name, webclient):
    if device_name == "an unkown device":
        udn = 'fake-udn-no-device-has-this'
    else:
        device = test_context.get_device(device_name)
        udn = device.udn
    test_context.last_response = await webclient.get(f'/player/{udn}/volume')


@then(parsers.cfparse('the volume reported by the API of {device_name} is {volume:d}'))
@sync
async def check_renderer_volume_with_webapi(test_context, device_name, webclient, volume):
    device = test_context.get_device(device_name)
    udn = device.udn
    response = await webclient.get(f'/player/{udn}/volume')
    test_context.last_response = response
    assert response.status_code == 200
    assert response.json() == {'volume_percent': volume}


@then(parsers.cfparse('the client will be notified about the new volume {volume:d}'))
@sync
async def check_device_notification(event_bus_connection, volume):
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['volume_percent'] == volume


@then('an error has been reported')
def check_last_webclient_response(test_context):
    assert test_context.last_response.status_code >= 300