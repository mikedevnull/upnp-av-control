from aiohttp import web
import logging
import socket
from async_upnp_client import UpnpEventHandler, UpnpService, UpnpRequester, UpnpNotifyServer
from typing import Callable, Awaitable, Mapping, Optional
from datetime import timedelta
import http
import asyncio

_logger = logging.getLogger(__name__)

NotifyReceivedCallable = Callable[[Mapping[str, str], str], Awaitable[http.HTTPStatus]]


class AiohttpNotificationEndpoint(UpnpNotifyServer):
    """
    Notifcation receiver implemented using `aiohttp`.
    """
    DEFAULT_PORT = 51234

    def __init__(self, port: int = DEFAULT_PORT, public_ip: Optional[str] = None):
        self._port = port
        if public_ip is None:
            self._ip = socket.gethostbyname(socket.getfqdn())
        else:
            self._ip = public_ip
        self._app = web.Application()
        self._app.router.add_route('NOTIFY', '/', self._async_handle_notify)
        self._runner = web.AppRunner(self._app)
        self._site = None
        self._notify_callback = None

    async def _async_handle_notify(self, request):
        body = await request.content.read()
        body = body.decode('utf-8')
        _logger.debug('NOTIFY: %s', body)
        if self._notify_callback:
            status = await self._notify_callback(request.headers, body)
            return web.Response(status=status.value)
        return web.Response(status=200)

    async def async_start(self, callback: NotifyReceivedCallable):
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "0.0.0.0", self._port)
        self._notify_callback = callback
        await self._site.start()

    async def async_stop(self):
        await self._runner.shutdown()
        self._notify_callback = None

    @property
    def callback_url(self):
        return f'http://{self._ip}:{self._port}/'


class NotificationBackend(object):

    def __init__(self, endpoint: UpnpNotifyServer, requester: UpnpRequester):
        self._endpoint = endpoint
        self._handler = UpnpEventHandler(self._endpoint, requester)
        self._subscription_timeout = timedelta(seconds=120)
        # time until subscription renewals are send, a little bit less then the
        # timeout so we have some time for the renewal process _before_ the subscription
        # actually times out
        self._subscription_renewal_time = self._subscription_timeout / 2
        self._renew_subscriptions_task = None
        self._subscriptions = {}

    async def async_start(self):
        """
        Run the notifcation backend, meaning that it will also start the notification
        endpoint and then renew any event subscriptions as neccessary.
        """
        if self._renew_subscriptions_task is not None:
            # assume we're already running
            return
        await self._endpoint.async_start(self._handler.handle_notify)
        self._renew_subscriptions_task = asyncio.create_task(self._resubscription_loop())
        _logger.info('NotificationBackend started (%s)', self._endpoint.callback_url)

    async def async_stop(self):
        if self._renew_subscriptions_task is not None:
            _logger.debug('Unsubscribing from all service events')
            await self._handler.async_unsubscribe_all()

            self._renew_subscriptions_task.cancel()
            await self._renew_subscriptions_task
            self._renew_subscriptions_task = None
            await self._endpoint.async_stop()
            _logger.info('NotificationBackend stopped')

    async def _resubscription_loop(self):
        try:
            while True:
                _logger.debug('Renewing all event subscriptons')
                await asyncio.sleep(self._subscription_renewal_time.total_seconds())
                await self._handler.async_resubscribe_all()
        except asyncio.CancelledError:
            _logger.debug('Resubscription loop cancelled')
        except Exception:
            _logger.exception('Resubscription loop failed')
            raise

    async def subscribe(self, service: UpnpService):
        try:
            sid, actual_renewal_time = await self._handler.async_subscribe(service, self._subscription_timeout)
            _logger.info('Subscribed service %s upnp events (sid: %s)', service, sid)
            self._subscriptions[service] = {"sid": sid, "timeout": actual_renewal_time}
            return sid
        except Exception:
            _logger.exception('Subscription to service failed')
            raise

    async def unsubscribe(self, service: UpnpService):
        if service in self._subscriptions:
            sid = self._subscriptions[service]['sid']
            await self._handler.async_unsubscribe(sid)

            _logger.info('Unsubscribed service %s upnp events (sid: %s)', service, sid)
        else:
            _logger.warning('Cannot unsubscribe service %s, no known subscription')
