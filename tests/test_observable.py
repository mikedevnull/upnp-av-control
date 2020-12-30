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


@pytest.mark.asyncio
async def test_subscription_callback():
    callback1 = mock.AsyncMock()
    callback2 = mock.AsyncMock()
    subscription_cb = mock.AsyncMock()
    observable = oberserver.Observable[int]()
    observable.on_subscription_change = subscription_cb
    assert observable.on_subscription_change == subscription_cb
    subscription1 = await observable.subscribe(callback1)
    subscription_cb.assert_called_once_with(1)
    subscription2 = await observable.subscribe(callback2)
    subscription_cb.assert_called_with(2)
    await observable.notify(42)
    callback1.assert_called_once_with(42)
    callback2.assert_called_once_with(42)

    callback1.reset_mock()
    callback2.reset_mock()

    await subscription1.unsubscribe()
    subscription_cb.assert_called_with(1)
    await observable.notify(21)
    callback1.assert_not_called()
    callback2.assert_called_once_with(21)

    # unsubscribing twice is fine as well
    subscription_cb.reset_mock()
    await subscription1.unsubscribe()
    subscription_cb.assert_not_called()
    await subscription2.unsubscribe()
    subscription_cb.assert_called_once_with(0)
