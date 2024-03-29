from pytest_bdd import scenarios, when, then, parsers
from .async_utils import sync
import logging
from .common_steps import *  # noqa: F401, F403

_logger = logging.getLogger(__name__)

scenarios('media_renderer_api.feature')


def _format_playback_info_path(webclient, udn):
    return webclient.application.url_path_for('get_playback_info', udn=udn)


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
    uri = f'/api/player/{udn}/playback'
    test_context.last_response = await webclient.patch(uri, json={'volume_percent': volume})


@when(parsers.cfparse('the client requests the volume of {device_name}'))
@sync
async def query_renderer_volume(test_context, device_name, webclient):
    if device_name == "an unkown device":
        udn = 'fake-udn-no-device-has-this'
    else:
        device = test_context.get_device(device_name)
        udn = device.udn
    test_context.last_response = await webclient.get(f'/api/player/{udn}/playback')


@when(parsers.parse('the transport state of {device_name} changes to {devicestate}'), converters=dict(devicestate=str))
@sync
async def external_playback_state_changes(test_context, device_name, devicestate):
    device = test_context.get_device(device_name)
    await device.service('urn:schemas-upnp-org:service:AVTransport:1')._ext_set_transport_state(devicestate)


@then(parsers.cfparse('the volume reported by the API of {device_name} is {volume:d}'))
@sync
async def check_renderer_volume_with_webapi(test_context, device_name, webclient, volume):
    device = test_context.get_device(device_name)
    udn = device.udn
    response = await webclient.get(f'/api/player/{udn}/playback')
    test_context.last_response = response
    assert response.status_code == 200
    assert response.json()['volume_percent'] == volume


@then(parsers.cfparse('the client will be notified about the new volume {volume:d}'))
@sync
async def check_device_volume_notification(event_bus_connection, volume):
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['volume_percent'] == volume


@then(parsers.parse('the client will be notified about the new state {apistate}'), converters=dict(apistate=str))
@sync
async def check_device_transport_state_notification(event_bus_connection, apistate):
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['transport'] == apistate


@then(parsers.parse('the client will be notified about the current state of {renderer}'))
@sync
async def check_device_state_notification(test_context, event_bus_connection, renderer):
    dmr = test_context.get_device(renderer)
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['volume_percent'] == dmr.service("urn:schemas-upnp-org:service:RenderingControl:1").volume
    assert info['transport'] == dmr.service("urn:schemas-upnp-org:service:AVTransport:1").state


@then('an error has been reported')
def check_last_webclient_response(test_context):
    assert test_context.last_response.status_code >= 300
