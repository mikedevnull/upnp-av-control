from pydantic import create_model, BaseModel, Field
from pydantic.generics import GenericModel
from typing import Any
from ..core.typing_compat import Literal
from typing import List, Iterable, TypeVar, Generic, Optional, Mapping

AttributesModelT = TypeVar('AttributesModelT')
TypeNameT = TypeVar('TypeNameT')
DataModelT = TypeVar('DataModelT')


class LinksModel(BaseModel):
    self_link: Optional[str] = Field(alias='self')
    related: Optional[str]


class RelationshipModel(BaseModel):
    links: LinksModel


class DataModel(GenericModel, Generic[AttributesModelT, TypeNameT]):
    id: str
    type: TypeNameT
    attributes: AttributesModelT
    links: Optional[LinksModel]
    relationships: Optional[Mapping[str, RelationshipModel]]


class DataModelIn(GenericModel, Generic[AttributesModelT, TypeNameT]):
    id: str
    type: TypeNameT
    attributes: AttributesModelT


class ResponseModel(GenericModel, Generic[DataModelT]):
    data: DataModelT


class RequestModel(GenericModel, Generic[DataModelT]):
    data: DataModelT


def create_request_model(type_name: str, payload_model: Any):
    PayloadModel = create_model(f'RequestPayload[{type_name}]',
                                type=(Literal[type_name], ...),
                                attributes=(payload_model, ...))
    RequestModel = create_model(f'Request[{type_name}]', data=(PayloadModel, ...))
    return RequestModel


def create_request_patch_model(type_name: str, PayloadModel: BaseModel):
    class OptionalPayloadModel(PayloadModel):
        ...

    for field in OptionalPayloadModel.__fields__.values():
        field.required = False

    OptionalPayloadModel.__name__ = f'Optional{BaseModel.__name__}'
    D = DataModelIn[OptionalPayloadModel, Literal[type_name]]
    return RequestModel[D]


def create_response_model(type_name: str, PayloadModel):
    D = DataModel[PayloadModel, Literal[type_name]]
    R = ResponseModel[D]

    def factory(id: str, payload: PayloadModel, self_link=None, relationships=None):
        data = {'type': type_name, 'id': id, 'attributes': payload}
        if self_link is not None:
            data['links'] = {'self': self_link}
        if relationships is not None:
            data['relationships'] = relationships
        return ResponseModel(data=data)

    R.create = staticmethod(factory)
    return R


def create_list_response_model(type_name: str, id_field: str, PayloadModel):
    D = DataModel[PayloadModel, Literal[type_name]]
    R = ResponseModel[List[D]]

    def factory(payload: Iterable[PayloadModel], links_factory=None, relationships=None):
        data = [{'type': type_name, 'id': d.__getattribute__(id_field), 'attributes': d} for d in payload]
        if links_factory is not None:
            for index, d in enumerate(payload):
                data[index]['links'] = links_factory(d)
        return ResponseModel(data=data)

    R.create = staticmethod(factory)
    return R
