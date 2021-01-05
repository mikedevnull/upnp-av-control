import asyncio
from pydantic import BaseModel, ValidationError
from typing import Optional, Any, Union, List, Literal
import json

JsonRPCParamType = Union[List[Any], dict[str, Any]]


class JsonRPCRequest(BaseModel):
    jsonrpc: Literal['2.0']
    method: str
    id: Union[int, str]
    params: Optional[JsonRPCParamType]


class JsonRPCNotification(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    method: str
    params: Optional[Any]


class JsonRPCResponse(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    result: Any
    id: Union[int, str]


class JsonRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any]


JSONRPC_PARSE_ERROR = JsonRPCError(code=-32700, message='Parse error')
JSONRPC_INVALID_REQUEST = JsonRPCError(code=-32600, message='Invalid request')
JSONRPC_METHOD_NOT_FOUND = JsonRPCError(code=-32601, message='Method not found')


class JsonRPCException(ValueError):
    def __init__(self, error: JsonRPCError, id=None):
        super().__init__()
        self.rpcerror = error
        self.rpcid = id

    def to_response(self):
        return JsonRPCErrorResponse(error=self.rpcerror, id=self.rpcid)


class JsonRPCErrorResponse(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    error: JsonRPCError
    id: Union[int, str]


def parse_jsonrpc_request(payload: str):
    parsed = {}
    try:
        parsed = json.loads(payload)
        return JsonRPCRequest(**parsed)
    except json.JSONDecodeError:
        raise JsonRPCException(error=JSONRPC_PARSE_ERROR)
    except ValidationError:
        id = None
        if 'id' in parsed:
            id = parsed['id']
        raise JsonRPCException(error=JSONRPC_INVALID_REQUEST, id=id)


class WebsocketEventBus(object):
    def __init__(self):
        self._queue = asyncio.Queue()

    def accept(self, websocket):
        pass

    def disconnect(self, websocket):
        pass

    def notify(self, message, category):
        pass
