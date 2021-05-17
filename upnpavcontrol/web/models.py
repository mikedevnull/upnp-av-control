from pydantic import BaseModel, Field
from ..core.discovery.registry import DiscoveryEventType


class DeviceModel(BaseModel):
    friendly_name: str = Field(alias="name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
