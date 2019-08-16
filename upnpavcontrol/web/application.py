from fastapi import FastAPI, Depends
from pydantic import BaseModel
import logging

app = FastAPI()

_av_control_point_instance = None


class RendererDevice(BaseModel):
    udn: str


class PlaybackInfo(BaseModel):
    player: str = None
    volume: int = None


def av_control_point():
    logging.info('av control point dep requested')
    return _av_control_point_instance


def _format_device(device):
    return {'name': device.upnp_device.friendly_name, 'udn': device.udn}


@app.get('/player/devices')
def device_list(av_cp=Depends(av_control_point)):
    return {'data': [_format_device(s) for s in av_cp.mediarenderers]}


@app.put('/player/device')
def set_active_player(device: RendererDevice, av_cp=Depends(av_control_point)):
    logging.info('Select device: %s', device.udn)
    av_cp.set_renderer(device.udn)


@app.get('/player', response_model=PlaybackInfo)
async def current_playback_info(av_cp=Depends(av_control_point)):
    if av_cp.mediarenderer is None:
        return {'player': None}
    else:
        volume = await av_cp.mediarenderer.get_volume()
        return {'player': av_cp.mediarenderer.udn, 'volume': volume}
