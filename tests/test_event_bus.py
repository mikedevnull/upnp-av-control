from upnpavcontrol.core.discovery.events import DiscoveryEventType
import pytest
from upnpavcontrol.web.models import DiscoveryEvent


@pytest.mark.asyncio
async def test_device_found_event_broadcast(webapi_client):
    app = webapi_client.application
    event_bus = app.event_bus
    async with webapi_client.websocket_connect('/ws/events') as websocket1:
        event = await websocket1.receive_json()
        assert event == {'version': '0.0.1'}
        async with webapi_client.websocket_connect('/ws/events') as websocket2:
            event = await websocket2.receive_json()
            assert event == {'version': '0.0.1'}

            event = DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE, udn='1234-5678-9')
            await event_bus.broadcast_event(event.json())

            event1 = await websocket1.receive_json()
            event2 = await websocket2.receive_json()
            assert event1['event_type'] == 'NEW_DEVICE'
            assert event1['udn'] == '1234-5678-9'
            assert event2['event_type'] == 'NEW_DEVICE'
            assert event2['udn'] == '1234-5678-9'
