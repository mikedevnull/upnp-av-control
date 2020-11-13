from pydantic import BaseModel
from ..core.discovery.registry import DiscoveryEventType


class DiscoveryEvent(BaseModel):
    event_type: DiscoveryEventType
    udn: str
