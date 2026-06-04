"""FastAPI application for ride sharing service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.shared.api.register import register_v1_routes

app = FastAPI(
    title="Ride Sharing API",
    version="0.1.0",
    description="A modern ride sharing application API",
)

register_v1_routes(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200, content={"status": "healthy", "service": "ride-sharing-app"}
    )
