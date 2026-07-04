from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.shared.api.register import register_v1_routes
from src.shared.db.redis_manager import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis_client()

    # Verify Redis is reachable
    await redis_client.ping()

    try:
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    title="Ride Sharing API",
    version="0.1.0",
    description="A modern ride sharing application API",
    lifespan=lifespan,
)

register_v1_routes(app)


@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "ride-sharing-app",
        },
    )
