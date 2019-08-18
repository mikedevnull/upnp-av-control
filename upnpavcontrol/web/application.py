from fastapi import FastAPI
from pydantic import BaseModel
import logging


class AVControlPointAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._av_control_point = None

    @property
    def av_control_point(self):
        return self._av_control_point

    @av_control_point.setter
    def av_control_point(self, control_point):
        self._av_control_point = control_point


app = AVControlPointAPI()


class RendererDevice(BaseModel):
    udn: str


class PlaybackInfo(BaseModel):
    player: str = None
    volume: int = None


def _format_device(device):
    return {'name': device.upnp_device.friendly_name, 'udn': device.udn}


@app.get('/player/devices')
def device_list():
    return {'data': [_format_device(s)
                     for s in app.av_control_point.mediarenderers]}


@app.put('/player/device')
def set_active_player(device: RendererDevice):
    logging.info('Select device: %s', device.udn)
    app.av_control_point.set_renderer(device.udn)


@app.get('/player', response_model=PlaybackInfo)
async def current_playback_info():
    if app.av_control_point.mediarenderer is None:
        return {'player': None}
    else:
        volume = await app.av_control_point.mediarenderer.get_volume()
        return {'player': app.av_control_point.mediarenderer.udn,
                'volume': volume}
