import pytest
from . import mock_utils
from . import device_mocks


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
    cp = webapi_client.application.av_control_point
    mocked_renderer = device_mocks.addMockedMediaRenderer(cp)
    mocked_renderer.rendering_control.action(
        'GetVolume').mock.return_value = {'CurrentVolume': 42}

    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] is None

    response = await webapi_client.put('/player/device',
                                       json={'udn': mocked_renderer.udn})
    assert response.status_code == 200
    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] == mocked_renderer.udn
    assert playbackInfo['volume'] == 42

    response = await webapi_client.put('/player/device',
                                       json={'udn': "fake-unkown-invalid-uid"})
    assert response.status_code == 400
    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] == mocked_renderer.udn
    assert playbackInfo['volume'] == 42


@pytest.mark.asyncio
async def test_set_volume(webapi_client):
    cp = webapi_client.application.av_control_point
    mocked_renderer = device_mocks.addMockedMediaRenderer(cp)

    # setting volume without an active player is an error
    response = await webapi_client.put('/player/volume',
                                       json={'volume_percent': 21})
    assert response.status_code == 404

    cp.set_renderer(mocked_renderer.udn)
    response = await webapi_client.put('/player/volume',
                                       json={'volume_percent': 21})
    assert response.status_code == 204
    volume_action = mocked_renderer.rendering_control.action('SetVolume')
    volume_action.mock.assert_called_once_with(InstanceID=0, Channel='Master',
                                               DesiredVolume=21)

    volume_action.mock.reset_mock()
    response = await webapi_client.put('/player/volume',
                                       json={'volume_percent': 101})
    assert response.status_code == 422
    volume_action.mock.assert_not_called()


@pytest.mark.asyncio
async def test_server_device_list(webapi_client):
    await mock_utils.find_dummy_renderer_server(
        webapi_client.application.av_control_point)
    response = await webapi_client.get('/library/devices')
    assert response.status_code == 200
    devices = response.json()['data']
    assert len(devices) == 1
    device = devices[0]
    assert device['name'] == 'Footech Media Server [MyFancyCollection]'
    assert device['udn'] == 'uuid:f5b1b596-c1d2-11e9-af8b-705681aa5dfd'
    device_links = device['links']
    assert device_links['browse'] == webapi_client.application.url_path_for(
        'browse_library', udn=device['udn'])
