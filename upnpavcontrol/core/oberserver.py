from typing import Callable, Awaitable, TypeVar, Generic, Dict
import asyncio

T = TypeVar('T')


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
    """
    def __init__(self):
        self._subscriptions: Dict[Subscription, Callable[[T], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, subscriber: Callable[[T], Awaitable[None]]) -> Subscription:
        """
        Subscribe an async callable that will be invoked when the observable wants to notify its subscribers.

        If the callable raises an exception, it will be automatically removed from the list of subscribers
        and will not receive any further notifications.

        Returns a `Subscription` handle that can be used to unsubscubsribe from notifcations
        """
        subscription = Subscription(self)
        self._subscriptions[subscription] = subscriber
        return subscription

    async def notify(self, payload: T):
        """
        Notify all subscribers, forwarding the given `playload`
        """
        subscriptions = []
        tasks = []
        async with self._lock:
            for subscription, callable in self._subscriptions.items():
                subscriptions.append(subscription)
                tasks.append(callable(payload))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                await self.unsubscribe(subscriptions[idx])

    async def unsubscribe(self, subscription: Subscription):
        """
        Remove the callable linked to the given subscription.
        """
        async with self._lock:
            if subscription in self._subscriptions:
                self._subscriptions.pop(subscription)
        subscription.reset()
