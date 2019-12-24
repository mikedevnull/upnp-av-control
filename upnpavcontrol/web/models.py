from pydantic import BaseModel
from ..core.discover import DiscoveryEventType


class DiscoveryEvent(BaseModel):
    event_type: DiscoveryEventType
    udn: str
