from fastapi import APIRouter
from server.routers.knowledge.add import router as add_router


router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"]
)

router.include_router(add_router)
