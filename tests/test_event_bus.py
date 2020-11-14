import pytest


@pytest.mark.asyncio
async def test_device_found_event(webapi_client, mocked_device_registry):
    async with webapi_client.websocket_connect('/ws/events') as websocket1:
        event = await websocket1.receive_json()
        assert event == {'version': '0.0.1'}
        async with webapi_client.websocket_connect('/ws/events') as websocket2:
            event = await websocket2.receive_json()
            assert event == {'version': '0.0.1'}

            trigger_event = await mocked_device_registry.trigger_renderer_alive()

            event1 = await websocket1.receive_json()
            event2 = await websocket2.receive_json()
            assert event1['event_type'] == 'NEW_DEVICE'
            assert event1['udn'] == trigger_event.udn
            assert event2['event_type'] == 'NEW_DEVICE'
            assert event2['udn'] == trigger_event.udn
