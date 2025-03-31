from fastapi import APIRouter, Query

from app.api.hello.schemas import HelloResponse
from app.api.hello.service import generate_greeting

# Create router
router = APIRouter(tags=["greetings"])


@router.get("/hello", response_model=HelloResponse)
async def hello(
    name: str = Query(None, description="Optional name for personalized greeting")
):
    """
    Returns a greeting message.
    """
    message = generate_greeting(name)
    return HelloResponse(message=message)
