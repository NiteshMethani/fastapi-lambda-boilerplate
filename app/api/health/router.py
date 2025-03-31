from fastapi import APIRouter

from app.api.health.schemas import HealthResponse

# Create router
router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    """
    return HealthResponse(status="healthy")
