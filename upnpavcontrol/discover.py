from .mediaserver import MediaServer
from .mediarenderer import MediaRenderer
from netdisco import ssdp
import re

media_server_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaServer:[1-9]')
media_renderer_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaRenderer:[1-9]')


def scan(timeout=3):
    results = ssdp.scan(timeout)
    servers = []
    renderers = []
    for device in results:
        try:
            if media_server_regex.match(device.st):
                server = MediaServer(device.location)
                servers.append(server)
            elif media_renderer_regex.match(device.st):
                renderer = MediaRenderer(device.location)
                renderers.append(renderer)
        except Exception:
            # Todo: log ignored device
            pass

    return servers, renderers
