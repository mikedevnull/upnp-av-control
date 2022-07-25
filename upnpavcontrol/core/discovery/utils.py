import re

_media_server_regex = re.compile(r'urn:schemas-upnp-org:device:MediaServer:[1-9]')
_media_renderer_regex = re.compile(r'urn:schemas-upnp-org:device:MediaRenderer:[1-9]')
_media_device_type_regex = re.compile(r'urn:schemas-upnp-org:device:Media(Server|Renderer):[1-9]')


def is_media_server(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is a MediaServer.

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaServer device, False otherwise
    """
    return _media_server_regex.match(device_type) is not None


def is_media_renderer(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is a MediaRenderer.

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaRenderer device, False otherwise
    """
    return _media_renderer_regex.match(device_type) is not None


def is_media_device(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is either a MediaRenderer or MediaServer

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaServer or MediaRenderer device, False otherwise
    """
    return _media_device_type_regex.match(device_type) is not None


def udn_from_usn(usn: str, device_type: str):
    """
    Extract the device UUID from a Unique Service Name.

    This only works for USNs that describe devices include the device type, not services or root devices

    Parameters
    -----------
    usn : str
        Unique Service Name in the form 'uuid:{device-UUID}::rn:schemas-upnp-org:device:{deviceType}:{ver}'
    device_type : str
        Device type descriptor in the form 'urn:schemas-upnp-org:device:{deviceType}:{ver}'

    Returns
    -------
    str
        Device UUID
    """
    return usn.replace(f'::{device_type}', '').lstrip('uuid:')
