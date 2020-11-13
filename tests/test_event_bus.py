import pytest
from upnpavcontrol.core.discovery import utils


@pytest.mark.asyncio
async def test_device_found_event(webapi_client, mocked_device_registry):
    async with webapi_client.websocket_connect('/ws/events') as websocket1:
        event = await websocket1.receive_json()
        assert event == {'version': '0.0.1'}
        async with webapi_client.websocket_connect('/ws/events') as websocket2:
            event = await websocket2.receive_json()
            assert event == {'version': '0.0.1'}

            renderer_ssdp = await mocked_device_registry.trigger_renderer_alive()

            event1 = await websocket1.receive_json()
            event2 = await websocket2.receive_json()
            assert event1['event_type'] == 'NEW_DEVICE'
            assert event1['udn'] == utils.udn_from_usn(renderer_ssdp['USN'], renderer_ssdp['NT'])
            assert event2['event_type'] == 'NEW_DEVICE'
            assert event2['udn'] == utils.udn_from_usn(renderer_ssdp['USN'], renderer_ssdp['NT'])
