import pytest
import urllib.parse


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
async def test_get_volume(webapi_client, mocked_renderer_device):
    response = await webapi_client.get('/player/unkown-device-udn/volume')
    assert response.status_code == 404

    mocked_renderer_device.rendering_control.action('GetVolume').mock.return_value = {'CurrentVolume': 42}
    volume_uri = f'/player/{mocked_renderer_device.udn}/volume'
    response = await webapi_client.get(volume_uri)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_volume(webapi_client, mocked_renderer_device):
    response = await webapi_client.put('/player/unkown-device-udn/volume', json={'volume_percent': 21})
    assert response.status_code == 404

    volume_uri = f'/player/{mocked_renderer_device.udn}/volume'
    response = await webapi_client.put(volume_uri, json={'volume_percent': 21})
    assert response.status_code == 204
    volume_action = mocked_renderer_device.rendering_control.action('SetVolume')
    volume_action.mock.assert_called_once_with(InstanceID=0, Channel='Master', DesiredVolume=21)

    volume_action.mock.reset_mock()
    response = await webapi_client.put(volume_uri, json={'volume_percent': 101})
    assert response.status_code == 422
    volume_action.mock.assert_not_called()


@pytest.mark.asyncio
async def test_server_device_list(webapi_client, mocked_server_device):
    response = await webapi_client.get('/library/devices')
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) == 1
    device = devices[0]
    assert device['friendly_name'] == mocked_server_device.friendly_name
    udn = urllib.parse.unquote_plus(device['udn'])
    assert udn == mocked_server_device.udn
