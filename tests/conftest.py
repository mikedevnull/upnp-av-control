import pytest
from upnpavcontrol.core import discover
from .mock_utils import create_test_advertisement_listener
from .mock_utils import mock_async_search, create_test_requester
from .mock_utils import UpnpTestAdvertisementListener


@pytest.fixture
def mocked_device_registry():
    return discover.DeviceRegistry(
        create_advertisement_listener=create_test_advertisement_listener,
        create_requester=create_test_requester)


@pytest.fixture
def mock_discovery_backend(monkeypatch):
    monkeypatch.setattr(discover, 'UpnpAdvertisementListener',
                        UpnpTestAdvertisementListener)
    monkeypatch.setattr(discover, 'AiohttpRequester', create_test_requester)


@pytest.fixture
def mock_scanned_devices(monkeypatch):
    monkeypatch.setattr(discover, 'async_search', mock_async_search)
