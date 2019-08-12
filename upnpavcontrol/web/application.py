from fastapi import FastAPI, Depends

app = FastAPI()

_av_control_point_instance = None


def av_control_point():
    return _av_control_point_instance


def _format_device(device):
    return {'name': device.upnp_device.friendly_name, 'udn': device.udn}


@app.get('/devices')
def device_list(av_cp=Depends(av_control_point)):
    servers = [_format_device(s) for s in av_cp.media_servers]
    renderer = [_format_device(s) for s in av_cp.media_renderer]
    return {'data': {'media_server': servers, 'media_renderer': renderer}}
