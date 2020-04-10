from fastapi import APIRouter
from . import library

router = APIRouter()
router.include_router(library.router, prefix='/library')
