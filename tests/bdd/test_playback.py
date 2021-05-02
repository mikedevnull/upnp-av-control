from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from .async_utils import sync
from functools import wraps
import asyncio
import logging

_logger = logging.getLogger(__name__)

scenarios('playback.feature')


@when(parsers.cfparse('the client requests to play item with id {object_id} from FooMediaServer on AcmeRenderer'))
@sync
async def play_object_on_dmr(test_context, object_id, webclient):
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    dms_device = test_context.get_device('FooMediaServer')
    dms_udn = dms_device.udn
    payload = {'data': {'type': 'playlistitem', 'attributes': {'dms': dms_udn, 'object_id': object_id}}}
    response = await webclient.post(f'/player/{dmr_udn}/queue', json=payload)
    assert response.status_code == 201


@then(parsers.cfparse('the client will be notified that {dmr} is now in {state} state'))
@sync
async def check_playback_state_notification(test_context, dmr, state, event_bus_connection):
    assert state in ('PLAYING', 'STOPPED')
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['transport'] == state


@then(parsers.cfparse('the playback state reported by the API of {dmr} is {state}'))
@sync
async def check_playback_state_with_api(test_context, dmr, state, webclient):
    assert state in ('PLAYING', 'STOPPED')
    dmr_device = test_context.get_device(dmr)
    response = await webclient.get(f'/player/{dmr_device.udn}/playback')
    assert response.status_code == 200
    data = response.json()['data']
    assert data['type'] == 'playbackinfo'
    assert data['id'] == dmr_device.udn
    assert data['attributes']['transport'] == state


@then(parsers.cfparse('the device {dmr} is playing item {object_id} from {dms}'))
def check_renderer_is_playing_object(test_context, dmr, object_id, dms):
    device = test_context.get_device('AcmeRenderer')
    av_transport = device.service('urn:schemas-upnp-org:service:AVTransport:1')
    assert av_transport.state == 'PLAYING'
    assert av_transport.current_uri == 'http://192.168.178.21:9002/music/2836/download.mp3?bitrate=320'