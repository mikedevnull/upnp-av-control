import pytest
from . import mock_utils


@pytest.fixture
async def webapi_client(mocked_device_registry):
    from upnpavcontrol.web import application
    from upnpavcontrol.core import AVControlPoint
    from async_asgi_testclient import TestClient
    test_control_point = AVControlPoint(mocked_device_registry)
    application.app.av_control_point = test_control_point

    async with TestClient(application.app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_renderer_device_list(webapi_client):
    await mock_utils.find_dummy_renderer_server(
        webapi_client.application.av_control_point)
    response = await webapi_client.get('/player/devices')
    assert response.status_code == 200
    assert response.json() == {'data': [{
        'name': 'FooRenderer',
        'udn': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306'}]
    }


@pytest.mark.asyncio
async def test_current_renderer(webapi_client):
    await mock_utils.find_dummy_renderer_server(
        webapi_client.application.av_control_point)
    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] is None

    response = await webapi_client.put('/player/device',
                                       json={'udn': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306'})
    assert response.status_code == 200
