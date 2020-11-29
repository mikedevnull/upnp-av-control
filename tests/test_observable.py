from upnpavcontrol.core import oberserver
from unittest import mock
import pytest


@pytest.mark.asyncio
async def test_basic_usage():
    callback1 = mock.AsyncMock()
    callback2 = mock.AsyncMock()
    observable = oberserver.Observable[int]()
    subscription1 = await observable.subscribe(callback1)
    subscription2 = await observable.subscribe(callback2)
    await observable.notify(42)
    callback1.assert_called_once_with(42)
    callback2.assert_called_once_with(42)

    callback1.reset_mock()
    callback2.reset_mock()

    await subscription1.unsubscribe()
    await observable.notify(21)
    callback1.assert_not_called()
    callback2.assert_called_once_with(21)

    # unsubscribing twice is fine as well
    await subscription1.unsubscribe()
    await subscription2.unsubscribe()


@pytest.mark.asyncio
async def test_callback_error_unsubscription():
    callback1 = mock.AsyncMock()
    callback2 = mock.AsyncMock()
    observable = oberserver.Observable[int]()
    subscription1 = await observable.subscribe(callback1)
    subscription2 = await observable.subscribe(callback2)

    callback1.side_effect = Exception('Something went wrong')
    await observable.notify(42)
    callback1.assert_called_once_with(42)
    callback2.assert_called_once_with(42)

    await observable.notify(42)

    callback1.reset_mock()
    callback2.reset_mock()

    await observable.notify(21)
    callback1.assert_not_called()
    callback2.assert_called_once_with(21)

    await subscription1.unsubscribe()
    await subscription2.unsubscribe()
