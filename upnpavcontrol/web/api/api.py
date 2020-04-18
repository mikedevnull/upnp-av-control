from fastapi import APIRouter
from . import library
from . import player
from . import media_proxy

router = APIRouter()
router.include_router(library.router, prefix='/library')
router.include_router(player.router, prefix='/player')
router.include_router(media_proxy.router, prefix='/proxy')
