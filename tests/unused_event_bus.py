from upnpavcontrol.core.mediarenderer import PlaybackInfo
from upnpavcontrol.core.oberserver import Observable
from upnpavcontrol.web.websocket_event_bus import WebsocketEventBus
from upnpavcontrol.web import json_rpc
from upnpavcontrol.core.discovery import MediaDeviceDiscoveryEvent, DiscoveryEventType, MediaDeviceType
import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI
import asyncio
from typing import Callable, Awaitable, cast


class FakeEventBusConnector(object):
    def __init__(self):
        self.discovery_observable = Observable[MediaDeviceDiscoveryEvent]()
        self.fake_renderer_observable_udn_1234 = Observable[PlaybackInfo]()

    async def subscribe_discovery_notifications(self, callback: Callable[[MediaDeviceDiscoveryEvent], Awaitable]):
        return await self.discovery_observable.subscribe(callback)

    async def subscribe_renderer_notifications(self, udn: str, callback: Callable[[str, PlaybackInfo], Awaitable]):
        if udn != '1234':
            raise KeyError('Unkown renderer UDN')

        async def f(playbackinfo):
            await callback(udn, playbackinfo)

        return await self.fake_renderer_observable_udn_1234.subscribe(f)


@pytest.fixture
async def event_bus():
    bus = WebsocketEventBus(FakeEventBusConnector())
    return bus


@pytest.fixture
async def event_bus_client(event_bus):
    app = FastAPI()
    app.add_websocket_route('/ws', event_bus.accept)

    async with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_new_connection(event_bus_client: TestClient):
    async with event_bus_client.websocket_connect('/ws') as websocket:
        response = await websocket.receive_json()
        notification = json_rpc.JsonRPCNotification(**response)
        assert notification.method == 'initialize'
        assert notification.params['version'] == '0.2.0'


async def _init_handshake(websocket):
    response = await websocket.receive_json()
    notification = json_rpc.JsonRPCNotification(**response)
    assert notification.method == 'initialize'
    assert notification.params['version'] == '0.2.0'


@pytest.mark.asyncio
async def test_unkown_method(event_bus_client: TestClient):
    async with event_bus_client.websocket_connect('/ws') as websocket1:
        await _init_handshake(websocket1)
        await websocket1.send_json({
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'foobar',
        })
        response = await websocket1.receive_json()
        assert response['id'] == 2
        assert 'error' in response
        assert response['error']['code'] == -32601


@pytest.mark.asyncio
async def test_subscribe_unsubscribe_discovery(event_bus_client: TestClient, event_bus):
    connector = cast(FakeEventBusConnector, event_bus._connector)
    async with event_bus_client.websocket_connect('/ws') as websocket1:
        await _init_handshake(websocket1)
        await websocket1.send_json({
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'subscribe',
            'params': {
                'category': 'discovery'
            }
        })
        response = await websocket1.receive_json()
        assert response['id'] == 2
        assert 'error' not in response

        await connector.discovery_observable.notify(
            MediaDeviceDiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                                      udn='1234',
                                      device_type=MediaDeviceType.MEDIARENDERER))

        raw_notifcation = await asyncio.wait_for(websocket1.receive_json(), 1)
        notification = json_rpc.JsonRPCNotification(**raw_notifcation)
        assert notification.method == 'new_device'
        assert notification.params['udn'] == '1234'
        assert notification.params['device_type'] == 'MediaRenderer'

        await websocket1.send_json({
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'unsubscribe',
            'params': {
                'category': 'discovery'
            }
        })
        response = await websocket1.receive_json()
        assert response['id'] == 3
        assert 'error' not in response

        await connector.discovery_observable.notify(
            MediaDeviceDiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                                      udn='1234',
                                      device_type=MediaDeviceType.MEDIARENDERER))
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(websocket1.receive_json(), 1)


@pytest.mark.asyncio
async def test_subscribe_unsubscribe_playbackinfo(event_bus_client: TestClient, event_bus):
    connector = cast(FakeEventBusConnector, event_bus._connector)
    async with event_bus_client.websocket_connect('/ws') as websocket1:
        await _init_handshake(websocket1)
        await websocket1.send_json({
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'subscribe',
            'params': {
                'category': 'playbackinfo',
                'udn': '1234'
            }
        })
        response = await websocket1.receive_json()
        assert response['id'] == 2
        assert 'error' not in response

        await connector.fake_renderer_observable_udn_1234.notify(PlaybackInfo(volume_percent=3))

        raw_notifcation = await asyncio.wait_for(websocket1.receive_json(), 1)
        notification = json_rpc.JsonRPCNotification(**raw_notifcation)
        assert notification.method == 'playbackinfo'
        assert notification.params['playbackinfo']['volume_percent'] == 3
        assert notification.params['udn'] == '1234'

        await websocket1.send_json({
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'unsubscribe',
            'params': {
                'category': 'playbackinfo',
                'udn': '1234'
            }
        })
        response = await websocket1.receive_json()
        assert response['id'] == 3
        assert 'error' not in response

        await connector.fake_renderer_observable_udn_1234.notify(PlaybackInfo(volume_percent=5))
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(websocket1.receive_json(), 1)
