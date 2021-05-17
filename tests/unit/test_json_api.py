from upnpavcontrol.web import json_api
import pydantic
import typing
import json


class TestDataModel(pydantic.BaseModel):
    id: int
    foo: int
    baz: str
    bar: typing.Optional[str]


def test_json_api_data_response():
    ResponseModel = json_api.create_response_model('testtype', TestDataModel)
    data = TestDataModel(id=2, foo=42, baz='hello')
    model = ResponseModel.create(data.id, data)
    raw = model.json()
    reparsed = json.loads(raw)
    assert 'data' in reparsed
    assert reparsed['data']['id'] == 2
    assert reparsed['data']['type'] == 'testtype'
    attributes = reparsed['data']['attributes']
    assert attributes['foo'] == 42
    assert attributes['baz'] == 'hello'


def test_json_api_list_data_response():
    ResponseModel = json_api.create_list_response_model('testtype', id_field='id', PayloadModel=TestDataModel)
    data = [TestDataModel(id=2, foo=42, baz='hello'), TestDataModel(id=3, foo=21, baz='world')]
    response = ResponseModel.create(data)
    raw = response.json()
    reparsed = json.loads(raw)
    assert 'data' in reparsed
    assert len(reparsed['data']) == 2
    print(reparsed['data'])
    d2 = next((x for x in reparsed['data'] if x['id'] == 2))
    assert d2['attributes']['baz'] == 'hello'
    assert d2['attributes']['foo'] == 42
    d3 = next((x for x in reparsed['data'] if x['id'] == 3))
    assert d3['attributes']['foo'] == 21
    assert d3['attributes']['baz'] == 'world'
