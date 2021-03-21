from pytest_bdd import scenarios, given, when, then, parsers
import pytest
from functools import wraps
from .fake_upnp import create_fake_device
import asyncio
from starlette.websockets import WebSocketDisconnect
import upnpavcontrol.core.discovery
import logging
from async_asgi_testclient import TestClient
from .context import TestContext
from .json_rpc_connection import JsonRPCTestConnection
from . import common_steps


@pytest.mark.asyncio
@pytest.fixture
def test_context(monkeypatch, event_loop):
    context = TestContext()
    monkeypatch.setattr(upnpavcontrol.core.discovery.scan, 'async_search', context.fake_async_search)

    return context


@pytest.mark.asyncio
@pytest.fixture
async def webclient(test_context, event_loop):
    from upnpavcontrol.web import application
    application.app.av_control_point = test_context.control_point
    async with TestClient(application.app) as webclient:
        yield webclient


@pytest.mark.asyncio
@pytest.fixture
async def event_bus_connection(webclient, event_loop):
    try:
        async with webclient.websocket_connect('/ws/events') as websocket:
            async with JsonRPCTestConnection(websocket) as rpcConnection:
                assert rpcConnection.state == 'connected'
                assert rpcConnection.api_version == '0.2.0'
                yield rpcConnection
    except WebSocketDisconnect:
        pass


@given(parsers.parse('a device {name} already present on the network'))
def a_device_foomediaserver_already_present_on_the_network(test_context, name):
    device = create_fake_device(name)
    test_context.add_device_to_network(name, device, notify=True)
