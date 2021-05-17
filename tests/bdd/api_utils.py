from urllib.parse import urlparse


async def get_playback_info_path(webclient, udn):
    response = await webclient.get(f'/api/player/{udn}')
    data = response.json()['data']
    uri = data['relationships']['playbackinfo']['links']['related']
    return urlparse(uri).path


async def get_playback_queue_path(webclient, udn):
    response = await webclient.get(f'/api/player/{udn}')
    data = response.json()['data']
    uri = data['relationships']['queue']['links']['related']
    return urlparse(uri).path
