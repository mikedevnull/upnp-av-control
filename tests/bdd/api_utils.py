from urllib.parse import urlparse, urlunparse


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


def extract_browse_path(data):
    uri = data['relationships']['browse']['links']['related']
    components = list(urlparse(uri))
    # delete scheme and host, but leave path, query params etc
    # required for test client to "retrieve" correct url
    components[0] = ''
    components[1] = ''
    return urlunparse(components)


async def get_browse_path(webclient, udn):
    response = await webclient.get(f'/api/library/{udn}')
    data = response.json()['data']
    return extract_browse_path(data)


async def get_metadata_path(webclient, udn):
    response = await webclient.get(f'/api/library/{udn}')
    data = response.json()['data']
    uri = data['relationships']['metadata']['links']['related']
    return urlparse(uri).path
