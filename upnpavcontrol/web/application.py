from fastapi import FastAPI
from .static_files_spa import StaticFilesSPA
from starlette.websockets import WebSocket
from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.core import notification_backend
from async_upnp_client.aiohttp import AiohttpRequester
from .websocket_event_bus import WebsocketEventBus, MediaDeviceDiscoveryCallback
from . import api
from . import settings
import aiohttp
import os
from typing import Optional


class AVControlPointAPI(FastAPI):

    def __init__(self, *args, **kwargs):
        super(AVControlPointAPI, self).__init__(*args, **kwargs)
        self._av_control_point: Optional[AVControlPoint] = None
        self.event_bus = WebsocketEventBus(self)
        self._aio_client_session: Optional[aiohttp.ClientSession] = None

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
        self._av_control_point = control_point

    async def subscribe_discovery_notifications(self, callback: MediaDeviceDiscoveryCallback):
        assert self._av_control_point is not None
        return await self._av_control_point.on_device_discovery_event(callback)

    async def subscribe_renderer_notifications(self, udn, callback):
        renderer = self._av_control_point.get_mediarenderer_by_UDN(udn)

        async def f(playbackinfo):
            await callback(udn, playbackinfo)

        return await renderer.subscribe_notifcations(f)


app = AVControlPointAPI()
app.include_router(api.router, prefix='/api')


@app.websocket('/api/ws/events')
async def websocket_endpoint(websocket: WebSocket):
    await app.event_bus.accept(websocket)


static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
static_files = StaticFilesSPA(directory=static_dir, html=True, check_dir=False)
app.mount('/', static_files, name='static')


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


@app.on_event("shutdown")
async def stop_av_control_point():
    if app._av_control_point is not None:
        await app.av_control_point.async_stop()
