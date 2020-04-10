from fastapi import APIRouter
from . import library
from . import player

router = APIRouter()
router.include_router(library.router, prefix='/library')
router.include_router(player.router, prefix='/player')
