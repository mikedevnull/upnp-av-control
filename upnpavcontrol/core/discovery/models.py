from .events import DiscoveryEventType
from enum import Enum
from pydantic import BaseModel
import typing


class MediaDeviceType(Enum):
    MEDIASERVER = 'MediaServer'
    MEDIARENDERER = 'MediaRenderer'


class MediaDeviceDiscoveryEvent(BaseModel):
    event_type: DiscoveryEventType
    device_type: MediaDeviceType
    udn: str
    friendly_name: typing.Optional[str]
