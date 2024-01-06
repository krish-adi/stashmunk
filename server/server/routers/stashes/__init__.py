from fastapi import APIRouter
from server.routers.stashes.create import router as create_router
from server.routers.stashes.delete import router as delete_router
from server.routers.stashes.list import router as list_router
from server.routers.stashes.info import router as info_router

router = APIRouter(
    prefix="/stashes",
    tags=["stashes"]
)

router.include_router(create_router)
router.include_router(delete_router)
router.include_router(list_router)
router.include_router(info_router)
