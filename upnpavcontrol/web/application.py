from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.core import notification_backend
from async_upnp_client.aiohttp import AiohttpRequester
from .broadcast_event_bus import BroadcastEventBus
from .models import DiscoveryEvent
from . import api
from . import settings
import aiohttp


class AVControlPointAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super(AVControlPointAPI, self).__init__(*args, **kwargs)
        self._av_control_point = None
        self._av_control_task = None
        self.event_bus = BroadcastEventBus()
        self._aio_client_session = None

    @property
    def aio_client_session(self):
        if self._aio_client_session is None:
            self._aio_client_session = aiohttp.ClientSession()
        return self._aio_client_session

    @property
    def av_control_point(self):
        return self._av_control_point

    @av_control_point.setter
    def av_control_point(self, control_point):
        if self._av_control_point is not None:
            self._av_control_point._devices.set_event_callback(None)
        self._av_control_point = control_point
        if self._av_control_point is not None:
            self._av_control_point._devices.set_event_callback(self._device_registry_callback)

    async def _device_registry_callback(self, event_type, device_udn):
        event = DiscoveryEvent(event_type=event_type, udn=device_udn)
        await self.event_bus.broadcast_event(event.json())


app = AVControlPointAPI()

app.include_router(api.router)


@app.websocket('/ws/events')
async def websocket_endpoint(websocket: WebSocket):
    await app.event_bus.accept(websocket)
    try:
        while True:
            # currently we don't expect any data coming in, so we discard it
            await websocket.receive_text()
    except WebSocketDisconnect:
        app.event_bus.remove_connection(websocket)


def create_control_point_from_settings():
    endpoint = notification_backend.AiohttpNotificationEndpoint(port=settings.EVENT_CALLBACK_PORT,
                                                                public_ip=settings.PUBLIC_IP)
    notification = notification_backend.NotificationBackend(endpoint, AiohttpRequester())
    cp = AVControlPoint(notifcation_backend=notification)
    return cp


@app.on_event("startup")
def setup_logging():
    import colorlog
    import logging
    level = logging.WARNING if settings.QUIET else logging.INFO
    level = logging.DEBUG if settings.DEBUG else level
    colorlog.basicConfig(level=level,
                         format='%(log_color)s%(levelname)s%(reset)s:%(yellow)s%(name)s%(reset)s: %(message)s')
    logging.getLogger('async_upnp_client').setLevel(logging.INFO)


@app.on_event("startup")
async def init_event_bus():
    # Use an existing control point instance, if any
    # This may be the case during testing, when
    # the control point might have been preconfigured and mocked
    if app.av_control_point is None:
        app.av_control_point = create_control_point_from_settings()
    await app.av_control_point.async_start()
    # Prime the push notification generator
    await app.event_bus.queue.asend(None)


@app.on_event("shutdown")
async def stop_av_control_point():
    if app._av_control_point:
        await app.av_control_point.async_stop()
