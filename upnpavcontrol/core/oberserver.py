from typing import Callable, Awaitable, TypeVar, Generic, Dict, List, Optional
import asyncio
import logging
from contextlib import asynccontextmanager

T = TypeVar('T')
_logger = logging.getLogger(__name__)


class Subscription(object):
    """
    A simple handle representing a subscription to observable notifications.

    Can be used to unsubscribe from notifications later on
    """

    def __init__(self, observable):
        self._observable = observable

    async def unsubscribe(self):
        """
        Unsubscribe from any future notifications.

        Does nothing if the subscriptions has already been unsubscribed
        """
        if self._observable is not None:
            await self._observable.unsubscribe(self)
            self.reset()

    def reset(self):
        """
        Reset the subscription handle _without_ unsubscribing.
        """
        self._observable = None


class Observable(Generic[T]):
    """
    A very simplistic observable implementation.

    Subscribe to a notification with any async callable.
    Upon registration, a subscription handle will be return that can be used to unsubsribe from notifications.

    Any callable that raises an exception will be automatically removed from the list of subscibers.

    It's possible to register an additional callback to react upon new/lost subscriptions.
    This makes it possible, for example, to stop additional services as long as no clients are subscribed.
    While the callback is invoked, the subscription count is guaranteed not to change.
    The callback must not add or remove subscriptions, as this will cause a deadlock.
    """

    def __init__(self, replay=False):
        self._subscriptions: Dict[Subscription, Callable[[T], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._change_callback_cb: Optional[Callable[[int], Awaitable[None]]] = None
        self._is_replaying = replay
        self._last_value: Optional[T] = None
        self._has_last_value = False

    @property
    def subscription_count(self):
        return len(self._subscriptions)

    @property
    def on_subscription_change(self) -> Optional[Callable[[int], Awaitable[None]]]:
        return self._change_callback_cb

    @on_subscription_change.setter
    def on_subscription_change(self, callback: Optional[Callable[[int], Awaitable[None]]]):
        self._change_callback_cb = callback

    async def subscribe(self, subscriber: Callable[[T], Awaitable[None]]) -> Subscription:
        """
        Subscribe an async callable that will be invoked when the observable wants to notify its subscribers.

        If the callable raises an exception, it will be automatically removed from the list of subscribers
        and will not receive any further notifications.

        Returns a `Subscription` handle that can be used to unsubscubsribe from notifcations
        """
        subscription = Subscription(self)
        async with self._lock:
            self._subscriptions[subscription] = subscriber
            if self._change_callback_cb is not None:
                await self._change_callback_cb(len(self._subscriptions))
            if self._has_last_value and self._is_replaying:
                await subscriber(self._last_value)
        return subscription

    async def notify(self, payload: T):
        """
        Notify all subscribers, forwarding the given `playload`
        """
        subscriptions = []
        tasks = []
        async with self._lock:
            self._last_value = payload
            self._has_last_value = True
            for subscription, callable in self._subscriptions.items():
                subscriptions.append(subscription)
                tasks.append(callable(payload))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                _logger.exception('Removing subscriber because of exception during execution')
                await self.unsubscribe(subscriptions[idx])

    async def unsubscribe(self, subscription: Subscription):
        """
        Remove the callable linked to the given subscription.
        """
        await self._batch_unsubscribe([subscription])

    async def _batch_unsubscribe(self, subscriptions: List[Subscription]):
        """
        Unsubscribe all given subscriptions in a single run.
        """
        async with self._lock:
            at_least_one_removed = False
            for subscription in subscriptions:
                if subscription in self._subscriptions:
                    self._subscriptions.pop(subscription)
                    at_least_one_removed = True
                subscription.reset()
            if at_least_one_removed and self._change_callback_cb is not None:
                await self._change_callback_cb(len(self._subscriptions))


@asynccontextmanager
async def wait_for_value_if(observerable: Observable[T], predicate: Callable[[T], bool], timeout: int = 15):
    """
    Async contextmanager that blocks on exit until some predicate for the observable value became true.

    Implmenetation as a contextmanager helps to avoid race conditions:
    ```
    # setup expectation by creating the context manager
    async with wait_for_value_if(obs, lamdba x: x==42):
        # carry out the action that will trigger that change
        await some_operation_that_will_eventually_change_obs_to_42()
    # on exit, the context manager will block until the predicate has been fullfilled
    ```
    """
    future = asyncio.get_running_loop().create_future()

    async def f(v: T):
        try:
            if predicate(v):
                future.set_result(True)
        except Exception as e:
            _logger.exception('predicate')
            future.set_exception(e)

    subscription = await observerable.subscribe(f)
    try:
        yield
        await asyncio.wait_for(future, timeout)
    finally:
        await subscription.unsubscribe()
