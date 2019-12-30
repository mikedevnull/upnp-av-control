import pytest


@pytest.mark.asyncio
async def test_renderer_device_list(webapi_client, mocked_renderer_device):
    response = await webapi_client.get('/player/devices')
    assert response.status_code == 200
    assert response.json() == {
        'data': [{
            'name': mocked_renderer_device.friendly_name,
            'udn': mocked_renderer_device.udn
        }]
    }


@pytest.mark.asyncio
async def test_current_renderer(webapi_client, mocked_renderer_device):
    mocked_renderer_device.rendering_control.action('GetVolume').mock.return_value = {'CurrentVolume': 42}

    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] is None

    response = await webapi_client.put('/player/device', json={'udn': mocked_renderer_device.udn})
    assert response.status_code == 200
    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] == mocked_renderer_device.udn
    assert playbackInfo['volume'] == 42

    response = await webapi_client.put('/player/device', json={'udn': "fake-unkown-invalid-uid"})
    assert response.status_code == 400
    response = await webapi_client.get('/player')
    assert response.status_code == 200
    playbackInfo = response.json()
    assert playbackInfo['player'] == mocked_renderer_device.udn
    assert playbackInfo['volume'] == 42


@pytest.mark.asyncio
async def test_set_volume(webapi_client, mocked_renderer_device):
    cp = webapi_client.application.av_control_point

    # setting volume without an active player is an error
    response = await webapi_client.put('/player/volume', json={'volume_percent': 21})
    assert response.status_code == 404

    await cp.set_renderer(mocked_renderer_device.udn)
    response = await webapi_client.put('/player/volume', json={'volume_percent': 21})
    assert response.status_code == 204
    volume_action = mocked_renderer_device.rendering_control.action('SetVolume')
    volume_action.mock.assert_called_once_with(InstanceID=0, Channel='Master', DesiredVolume=21)

    volume_action.mock.reset_mock()
    response = await webapi_client.put('/player/volume', json={'volume_percent': 101})
    assert response.status_code == 422
    volume_action.mock.assert_not_called()


@pytest.mark.asyncio
async def test_server_device_list(webapi_client, mocked_server_device):
    response = await webapi_client.get('/library/devices')
    assert response.status_code == 200
    devices = response.json()['data']
    assert len(devices) == 1
    device = devices[0]
    assert device['name'] == mocked_server_device.friendly_name
    assert device['udn'] == mocked_server_device.udn
    device_links = device['links']
    assert device_links['browse'] == webapi_client.application.url_path_for('browse_library', udn=device['udn'])
