import pytest
import pytest_asyncio
from starlette.websockets import WebSocketDisconnect
from async_asgi_testclient import TestClient
from .context import TestContext
from .json_rpc_connection import JsonRPCTestConnection


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def test_context(monkeypatch, event_loop):
    context = TestContext()

    # create webclient here already to ensure the control point will be started
    from upnpavcontrol.web import application
    application.app.av_control_point = context.control_point
    async with TestClient(application.app) as webclient:
        context.webclient = webclient
        yield context


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def webclient(test_context, event_loop):
    return test_context.webclient


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def event_bus_connection(webclient, event_loop):
    try:
        async with webclient.websocket_connect('/api/ws/events') as websocket:
            async with JsonRPCTestConnection(websocket) as rpcConnection:
                assert rpcConnection.state == 'connected'
                assert rpcConnection.api_version == '0.2.0'
                yield rpcConnection
    except WebSocketDisconnect:
        pass
