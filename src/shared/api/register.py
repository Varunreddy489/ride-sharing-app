from types import ModuleType

from fastapi import FastAPI

from src.modules.auth import auth_routes
from src.modules.drivers import driver_routes
from src.shared.api import ws_routes


def _register(uri_prefix: str, modules: list[ModuleType], app: FastAPI):
    for module in modules:
        app.include_router(module.router, prefix=uri_prefix)
    return app


def register_v1_routes(app: FastAPI) -> FastAPI:

    v1_modules: list[ModuleType] = [auth_routes, driver_routes, ws_routes]
    return _register("/v1", v1_modules, app)
