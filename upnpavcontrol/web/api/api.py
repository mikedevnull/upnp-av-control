from fastapi import APIRouter, Request
from . import library
from . import player
from . import media_proxy
from ..models import ApiInfo

router = APIRouter()
router.include_router(library.router, prefix='/library')
router.include_router(player.router, prefix='/player')
router.include_router(media_proxy.router, prefix='/proxy')


@router.get('/', response_model=ApiInfo)
def api_info(request: Request):
    return {
        'version': 1,
    }


@router.get('/list_endpoints/')
def list_endpoints(request: Request):
    url_list = [{'path': route.path, 'name': route.name} for route in request.app.routes]
    return url_list
