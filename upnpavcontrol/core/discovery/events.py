from enum import Enum
from dataclasses import dataclass
import typing


class DiscoveryEventType(Enum):
    """
    Different type of upnp events that might occur
    """
    NEW_DEVICE = 'NEW_DEVICE'
    DEVICE_UPDATE = 'DEVICE_UPDATE'
    DEVICE_LOST = 'DEVICE_LOST'


@dataclass(frozen=True)
class SSDPEvent:
    """
    Provides all required information to handle discovery
    events in a uniform way.
    This includes advertisements via SSDP (alive, update, bybye) and
    but also responses to search requests.

    Attributes
    ----------
    event_type : DiscoveryEventType
        The type of discovery represented by this event
    device_type : str
        A UPnP device type descriptor of the form 'urn:schemas-upnp-org:device:{deviceType}:{ver}'
    udn : str
        UUID of the device
    location: str or None
        URL to the UPnP description of the device. Only available for `NEW_DEVICE` or `DEVICE_UPDATE`
        event types.
    """
    event_type: DiscoveryEventType
    device_type: str
    udn: str
    location: typing.Optional[str] = None


@dataclass(frozen=True)
class MediaDeviceDiscoveryEvent:
    event_type: DiscoveryEventType
    device_type: str
    udn: str
    location: typing.Optional[str] = None
