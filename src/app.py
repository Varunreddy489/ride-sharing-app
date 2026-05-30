"""FastAPI application for ride sharing service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Ride Sharing API",
    version="0.1.0",
    description="A modern ride sharing application API"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "ride-sharing-app"}
    )


