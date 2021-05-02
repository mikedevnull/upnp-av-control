from pydantic import create_model
from typing import Any
from ..core.typing_compat import Literal


def create_request_model(type_name: str, payload_model: Any):
    PayloadModel = create_model(f'RequestPayload[{type_name}]',
                                type=(Literal[type_name], ...),
                                attributes=(payload_model, ...))
    RequestModel = create_model(f'Request[{type_name}]', data=(PayloadModel, ...))
    return RequestModel


def create_response_model(type_name: str, payload_model: Any):
    PayloadModel = create_model(f'ResponsePayload[{type_name}]',
                                type=(Literal[type_name], type_name),
                                id=(str, ...),
                                attributes=(payload_model, ...))
    ResponseModel = create_model(f'Response[{type_name}]', data=(PayloadModel, ...))

    def factory(id: str, payload: payload_model):
        data = {'id': id, 'attributes': payload}
        return ResponseModel(data=data)

    ResponseModel.create = staticmethod(factory)
    return ResponseModel
