from fastapi import FastAPI
from mangum import Mangum

from app.api.routes import router

# Create FastAPI application
app = FastAPI(  # This must be named "app" exactly
    title="FastAPI Lambda",
    description="FastAPI application deployed on AWS Lambda",
    version="0.1.0",
)

# Include API router
app.include_router(router, prefix="/api")

# Create Lambda handler
handler = Mangum(app)
