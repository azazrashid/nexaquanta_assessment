from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router
from app.core.cache import redis_cache
from app.core.config import config
from app.core.middlewares import AccessControlMiddleware


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Nexaquanta Assessment",
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
    )
    app_.add_middleware(AccessControlMiddleware)
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_routers(app_=app_)

    @app_.on_event("startup")
    async def startup():
        await redis_cache.connect()  # Connect to Redis on startup

    @app_.on_event("shutdown")
    async def shutdown():
        await redis_cache.close()

    return app_


app = create_app()
