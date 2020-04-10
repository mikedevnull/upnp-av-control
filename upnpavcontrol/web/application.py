from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from starlette.websockets import WebSocket, WebSocketDisconnect
import logging
from upnpavcontrol.core import AVControlPoint
from .broadcast_event_bus import BroadcastEventBus
from .models import DiscoveryEvent
from . import api


class AVControlPointAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super(AVControlPointAPI, self).__init__(*args, **kwargs)
        self._av_control_point = None
        self._av_control_task = None
        self.event_bus = BroadcastEventBus()

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


class RendererDevice(BaseModel):
    udn: str


class PlaybackInfo(BaseModel):
    player: str = None
    volume: int = None


def _format_device(device):
    return {'name': device.upnp_device.friendly_name, 'udn': device.udn}


@app.get('/player/devices')
def device_list():
    return {'data': [_format_device(s) for s in app.av_control_point.mediarenderers]}


@app.put('/player/device')
async def set_active_player(device: RendererDevice):
    try:
        logging.info('Select device: %s', device.udn)
        await app.av_control_point.set_renderer(device.udn)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


class Volume(BaseModel):
    volume_percent: int

    @validator('volume_percent')
    def volume_percent_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Volume out of range (0 <= volume <= 100)')
        return v


@app.put('/player/volume', status_code=204)
async def set_player_volume(volume: Volume):
    if app.av_control_point.mediarenderer is None:
        raise HTTPException(status_code=404)
    await app.av_control_point.mediarenderer.set_volume(volume.volume_percent)
    return ''


@app.get('/player', response_model=PlaybackInfo)
async def current_playback_info():
    if app.av_control_point.mediarenderer is None:
        return {'player': None}
    else:
        volume = await app.av_control_point.mediarenderer.get_volume()
        return {'player': app.av_control_point.mediarenderer.udn, 'volume': volume}


@app.websocket('/ws/events')
async def websocket_endpoint(websocket: WebSocket):
    await app.event_bus.accept(websocket)
    try:
        while True:
            # currently we don't expect any data coming in, so we discard it
            await websocket.receive_text()
    except WebSocketDisconnect:
        app.event_bus.remove_connection(websocket)


@app.on_event("startup")
async def init_event_bus():
    # Use an existing control point instance, if any
    # This may be the case during testing, when
    # the control point might have been preconfigured and mocked
    if app.av_control_point is None:
        app.av_control_point = AVControlPoint()
    await app.av_control_point.async_start()
    # Prime the push notification generator
    await app.event_bus.queue.asend(None)


@app.on_event("shutdown")
async def stop_av_control_point():
    if app._av_control_point:
        await app.av_control_point.async_stop()
