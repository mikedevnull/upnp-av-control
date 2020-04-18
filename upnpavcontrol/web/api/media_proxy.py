from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse
from itsdangerous import URLSafeSerializer
import logging

router = APIRouter()
_logger = logging.getLogger(__name__)


def encode_url_proxy_token(url):
    serializer = URLSafeSerializer('super-secret-key-fixme')
    return serializer.dumps({'url': url}, salt='urlproxy')


def get_media_proxy_url(url):
    from .api import router as api_router
    token = encode_url_proxy_token(url)
    url = api_router.url_path_for('proxy_request', token=token)
    _logger.debug(url)
    return url


def decode_url_proxy_token(token):
    serializer = URLSafeSerializer('super-secret-key-fixme')
    payload = serializer.loads(token, salt='urlproxy')
    return payload['url']


async def read_from_streamreader(stream):
    data = await stream.read()
    yield data


async def bytes_provider(data):
    yield data


@router.get('/{token}')
async def proxy_request(request: Request, token):
    url = decode_url_proxy_token(token)

    async with request.app.aio_client_session.get(url) as resp:
        data = await resp.content.read()
        _logger.info(resp)
        return StreamingResponse(bytes_provider(data), media_type=resp.content_type)
