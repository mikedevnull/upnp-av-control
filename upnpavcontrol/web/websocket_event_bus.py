from . import json_rpc
from typing import Callable, Awaitable
from upnpavcontrol.core.typing_compat import Protocol
from upnpavcontrol.core.discovery import MediaDeviceDiscoveryEvent
from upnpavcontrol.core.mediarenderer import PlaybackInfo
from upnpavcontrol.core.oberserver import Subscription
import logging
from contextlib import asynccontextmanager

_event_type_map = {'NEW_DEVICE': 'new_device', 'DEVICE_LOST': 'device_lost'}

MediaDeviceDiscoveryCallback = Callable[[MediaDeviceDiscoveryEvent], Awaitable]

_logger = logging.getLogger(__name__)


class EventBusConnector(Protocol):
    async def subscribe_discovery_notifications(self, callback: MediaDeviceDiscoveryCallback) -> Subscription:
        ...

    async def subscribe_renderer_notifications(self, udn: str, callback: Callable[[str, PlaybackInfo],
                                                                                  Awaitable]) -> Subscription:
        ...


class EventBusConnection(object):
    def __init__(self, websocket, connector: EventBusConnector):
        self._websocket = websocket
        self._connector = connector
        self._discovery_subscription = None
        self._playback_subscriptions = {}

    async def serve(self):
        await self._websocket.send_text(
            json_rpc.JsonRPCNotification(method='initialize', params={
                'version': '0.2.0'
            }).json())
        while True:
            try:
                raw_request = await self._websocket.receive_text()
                _logger.debug('Websocket recv: %s', raw_request)
                request = json_rpc.parse_jsonrpc_request(raw_request)
                response = await self._handle_request(request)
                await self._websocket.send_text(response.json())
            except json_rpc.JsonRPCException as e:
                await self._websocket.send_text(e.to_response().json())

    async def cleanup(self):
        if self._discovery_subscription:
            await self._discovery_subscription.unsubscribe()
            self._discovery_subscription = None
        for sub in self._playback_subscriptions.values():
            await sub.unsubscribe()
        self._playback_subscriptions.clear()

    async def _handle_request(self, request: json_rpc.JsonRPCRequest):
        if request.method not in ('subscribe', 'unsubscribe'):
            raise json_rpc.JsonRPCException(id=request.id, error=json_rpc.JSONRPC_METHOD_NOT_FOUND)
        if request.method == 'unsubscribe':
            return await self._handle_unsubscription(request)
        if request.method == 'subscribe':
            return await self._handle_subscription(request)
        return json_rpc.JsonRPCResponse(id=request.id, result=False)

    async def _handle_subscription(self, request):
        if request.params['category'] == 'discovery':
            if self._discovery_subscription is None:
                self._discovery_subscription = await self._connector.subscribe_discovery_notifications(
                    self._notify_discovery)
                return json_rpc.JsonRPCResponse(id=request.id, result=True)
        if request.params['category'] == 'playbackinfo':
            udn = request.params['udn']
            if udn not in self._playback_subscriptions:
                self._playback_subscriptions[udn] = await self._connector.subscribe_renderer_notifications(
                    udn, self._notifiy_playbackinfo)
                return json_rpc.JsonRPCResponse(id=request.id, result=True)
        return json_rpc.JsonRPCResponse(id=request.id, result=False)

    async def _handle_unsubscription(self, request):
        if request.params['category'] == 'discovery':
            if self._discovery_subscription is not None:
                await self._discovery_subscription.unsubscribe()
                self._discovery_subscription = None
                return json_rpc.JsonRPCResponse(id=request.id, result=True)
        if request.params['category'] == 'playbackinfo':
            udn = request.params['udn']
            if udn in self._playback_subscriptions:
                sub = self._playback_subscriptions.pop(udn)
                await sub.unsubscribe()
                return json_rpc.JsonRPCResponse(id=request.id, result=True)
        return json_rpc.JsonRPCResponse(id=request.id, result=False)

    async def _notify_discovery(self, event: MediaDeviceDiscoveryEvent):
        assert event.event_type.name in _event_type_map
        method = _event_type_map[event.event_type.name]
        msg = json_rpc.JsonRPCNotification(method=method, params=event.dict())
        _logger.debug('Sending discovery event "%s" for device %s', method, event.udn)
        await self._websocket.send_text(msg.json())

    async def _notifiy_playbackinfo(self, udn, playbackinfo):
        msg = json_rpc.JsonRPCNotification(method='playbackinfo', params={'udn': udn, 'playbackinfo': playbackinfo})
        _logger.debug('Sending playbackinfo event "%s" for device %s', playbackinfo, udn)
        await self._websocket.send_text(msg.json())


@asynccontextmanager
async def event_bus_connection(websocket, connector):
    _logger.info('accepted eventbus connection')
    connection = EventBusConnection(websocket, connector)
    try:
        yield connection
    finally:
        await connection.cleanup()
        _logger.info('eventbus connection closed')


class WebsocketEventBus(object):
    def __init__(self, connector: EventBusConnector):
        self._notification_sockets = []
        self._connector = connector

    async def accept(self, websocket):
        _logger.debug('incoming event bus websocket connection')
        await websocket.accept()
        async with event_bus_connection(websocket, self._connector) as connection:
            await connection.serve()
