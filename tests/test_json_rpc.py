from upnpavcontrol.web.json_rpc import JsonRPCResponse, parse_jsonrpc_request, JsonRPCNotification, JsonRPCException
import json
import pytest
import typing


def test_jsonrpc_request_parsing():
    msg = parse_jsonrpc_request('{"jsonrpc": "2.0", "id": 1, "method": "subscribe"}')
    assert msg.id == 1
    assert msg.method == 'subscribe'
    assert msg.params is None


def test_jsonrpc_request_param_list():
    msg = parse_jsonrpc_request('{"jsonrpc": "2.0", "id": 1, "params": [1, "hello"], "method": "subscribe"}')
    assert msg.id == 1
    assert msg.method == 'subscribe'
    assert msg.params is not None
    assert len(msg.params) == 2
    assert typing.cast(list, msg.params)[0] == 1
    assert typing.cast(list, msg.params)[1] == 'hello'


def test_jsonrpc_request_param_dict():
    msg = parse_jsonrpc_request(
        '{"jsonrpc": "2.0", "id": 1, "params": {"value":1, "greeting":"hello"}, "method": "subscribe"}')
    assert msg.id == 1
    assert msg.method == 'subscribe'
    assert msg.params is not None
    assert len(msg.params) == 2
    assert typing.cast(dict, msg.params)['value'] == 1
    assert typing.cast(dict, msg.params)['greeting'] == 'hello'


def test_jsonrpc_request_no_id():
    with pytest.raises(ValueError):
        parse_jsonrpc_request('{"jsonrpc": "2.0", "method": "subscribe"}')


def test_jsonrpc_request_invalid_json():
    with pytest.raises(JsonRPCException) as exc_info:
        parse_jsonrpc_request('{jsonrpc: "2.0", "method", "subscribe"}')
        response = exc_info.value.to_response()
        assert response.id is None
        assert response.error.code == -36700
        assert response.error.message == 'Parse error'


def test_jsonrpc_request_no_method():
    with pytest.raises(JsonRPCException) as exc_info:
        parse_jsonrpc_request('{"jsonrpc": "2.0",  "id": 1}')
        response = exc_info.value.to_response()
        assert response.id == 1
        assert response.error.code == -36600
        assert response.error.message == 'Invalid request'


def test_jsonrpc_request_no_jsonrpc():
    with pytest.raises(JsonRPCException) as exc_info:
        parse_jsonrpc_request('{"method": "subscribe", "id": 1}')
        response = exc_info.value.to_response()
        assert response.id == 1
        assert response.error.code == -36600
        assert response.error.message == 'Invalid request'


def test_jsonrpc_notification():
    msg = JsonRPCNotification(method="update", params=[1])
    payload = msg.json()
    reparsed_msg = json.loads(payload)
    assert reparsed_msg['jsonrpc'] == '2.0'
    assert reparsed_msg['method'] == 'update'
    assert reparsed_msg['params'] == [1]


def test_jsonrpc_response():
    response = JsonRPCResponse(id=99, result='foo')
    assert response.id == 99
    assert response.result == 'foo'
    payload = response.json()
    reparsed_msg = json.loads(payload)
    assert reparsed_msg['jsonrpc'] == '2.0'
    assert reparsed_msg['id'] == 99
    assert reparsed_msg['result'] == 'foo'
