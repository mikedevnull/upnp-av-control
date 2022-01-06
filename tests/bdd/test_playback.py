from pytest_bdd import scenarios, when, then, parsers, given
from .async_utils import sync
import logging
from .common_steps import *  # noqa: F401, F403
from upnpavcontrol.web.api.library import create_library_item_id

_logger = logging.getLogger(__name__)

scenarios('playback.feature')


def parse_data_table(tabledata: str):
    tablelines = [[c.strip() for c in line.strip().split('|')[1:-1]] for line in tabledata.splitlines()]
    header = tablelines[0]
    table = [dict(zip(header, entry)) for entry in tablelines[1:]]
    return table


async def _wait_for_playback_state_notification(event_bus_connection, state):
    assert state in ('PLAYING', 'STOPPED')
    event = await event_bus_connection.wait_for_notification()
    assert event.method == 'playbackinfo'
    info = event.params['playbackinfo']
    assert info['transport'] == state


@given('the playback queue for AcmeRenderer is empty')
@sync
async def clear_playback_queue(test_context):
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    pc = test_context.control_point.get_controller_for_renderer(dmr_udn)
    pc.queue.clear()


@given(parsers.cfparse('the playback queue of AcmeRenderer already contains the following items:\n{table}'))
@sync
async def preset_playback_queue(test_context, table):
    data = parse_data_table(table)
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    pc = test_context.control_point.get_controller_for_renderer(dmr_udn)
    pc.queue.clear()
    for entry in data:
        dms_udn = test_context.get_device(entry['dms']).udn
        object_id = entry['item id']
        pc.queue.append(dms_udn, object_id, title=None)


@when(parsers.cfparse('the client adds item with id {object_id} from FooMediaServer to AcmeRenderer playback queue'))
@sync
async def enqueue_on_dmr(test_context, object_id, webclient):
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    dms_device = test_context.get_device('FooMediaServer')
    dms_udn = dms_device.udn

    item_id = create_library_item_id(dms_udn, object_id)
    payload = {'items': [{"id": item_id}]}
    uri = f"/api/player/{dmr_udn}/queue"

    response = await webclient.post(uri, json=payload)
    assert response.status_code == 201


@when(parsers.cfparse('the client replaces the content of the queue of AcmeRenderer with the following items:\n{table}')
      )
@sync
async def set_queue_on_dmr(test_context, table, webclient):
    data = parse_data_table(table)
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    items = []
    for entry in data:
        dms_udn = test_context.get_device(entry['dms']).udn
        object_id = entry['item id']
        item_id = create_library_item_id(dms_udn, object_id)
        items.append({"id": item_id})
    payload = {'items': items}
    uri = f"/api/player/{dmr_udn}/queue"
    response = await webclient.put(uri, json=payload)
    assert response.status_code == 200


@when('the client starts playback on AcmeRenderer')
@sync
async def client_starts_playback(test_context, webclient):
    dmr_device = test_context.get_device('AcmeRenderer')
    dmr_udn = dmr_device.udn
    payload = {'transport': 'PLAYING'}
    uri = f"/api/player/{dmr_udn}/playback"
    response = await webclient.patch(uri, json=payload)
    assert response.status_code == 200


@when(parsers.cfparse('the client will be notified that {dmr} is now {state}'))
@sync
async def when_check_playback_state_notification(test_context, dmr, event_bus_connection, state):
    await _wait_for_playback_state_notification(event_bus_connection, state)


@when('the client read all pending notifications')
@sync
async def client_clear_all_event_bus_notifications(event_bus_connection):
    await event_bus_connection.clear_pending_notifications()


@when('AcmeRenderer finishes playback of current track')
@sync
async def renderer_finishes_current_track(test_context):
    dmr_device = test_context.get_device('AcmeRenderer')
    avt_service = dmr_device.service('urn:schemas-upnp-org:service:AVTransport:1')
    await avt_service._ext_set_transport_state('STOPPED')


@then(parsers.cfparse('the client will be notified that {dmr} is now in {state} state'))
@sync
async def then_check_playback_state_notification(test_context, dmr, state, event_bus_connection):
    await _wait_for_playback_state_notification(event_bus_connection, state)


@then(parsers.cfparse('the playback state reported by the API of {dmr} is {state}'))
@sync
async def check_playback_state_with_api(test_context, dmr, state, webclient):
    assert state in ('PLAYING', 'STOPPED')
    dmr_device = test_context.get_device(dmr)
    response = await webclient.get(f'/api/player/{dmr_device.udn}/playback')
    assert response.status_code == 200
    data = response.json()
    assert data['transport'] == state


@then(parsers.cfparse('the device {dmr} is playing item {object_id} from {dms}'))
@sync
async def check_renderer_is_playing_object(test_context, dmr, object_id, dms):
    dms_device = test_context.get_device(dms)
    server = test_context.control_point.get_mediaserver_by_UDN(dms_device.udn)
    didl = await server.browse_metadata(object_id)
    meta = didl.objects[0]
    device = test_context.get_device('AcmeRenderer')
    av_transport = device.service('urn:schemas-upnp-org:service:AVTransport:1')
    assert av_transport.state == 'PLAYING'
    assert av_transport.current_uri == meta.res[0].uri


@then(parsers.cfparse('the playback queue of {dmr} contains the following items:\n{table}'))
@sync
async def check_playback_queue_contents(test_context, dmr, table, webclient):
    expected_items = parse_data_table(table)
    dmr_device = test_context.get_device(dmr)
    response = await webclient.get(f'/api/player/{dmr_device.udn}/queue')
    assert response.status_code == 200
    data = response.json()
    items = data['items']
    assert len(items) == len(expected_items)
    for expected_entry, entry in zip(expected_items, items):
        dms_udn = test_context.get_device(expected_entry['dms']).udn
        object_id = expected_entry['item id']
        item_id = create_library_item_id(dms_udn, object_id)
        assert entry['id'] == item_id


@then(parsers.cfparse('the playback queue of {dmr} is empty'))
@sync
async def check_playback_queue_is_empty(test_context, dmr, webclient):
    dmr_device = test_context.get_device(dmr)
    response = await webclient.get(f'/api/player/{dmr_device.udn}/queue')
    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) == 0


@then('the playback queue current item index of AcmeRenderer is not defined')
@sync
async def check_playback_queue_current_item_not_defined(test_context, webclient):
    dmr_device = test_context.get_device('AcmeRenderer')
    response = await webclient.get(f'/api/player/{dmr_device.udn}/queue')
    assert response.status_code == 200
    data = response.json()
    assert data['current_item_index'] is None


@then(parsers.cfparse('the playback queue current item index of AcmeRenderer is {item_index:n}'))
@sync
async def check_playback_queue_current_item_is(test_context, item_index: int, webclient):
    dmr_device = test_context.get_device('AcmeRenderer')
    response = await webclient.get(f'/api/player/{dmr_device.udn}/queue')
    assert response.status_code == 200
    data = response.json()
    assert data['current_item_index'] == item_index
