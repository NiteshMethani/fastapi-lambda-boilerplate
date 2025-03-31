from fastapi import APIRouter

from app.api.health.router import router as health_router
from app.api.hello.router import router as hello_router

# Create main API router
router = APIRouter()

# Include feature routers
router.include_router(hello_router)
router.include_router(health_router)
