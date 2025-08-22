from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.api.routes import router as api_router
from app.database.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Application started and database tables created!")
    await init_db()
    yield  # This will pause here until the app shuts down
    # Shutdown: Dispose of the engine
    # await engine.dispose()
    print("🛑 Application shutting down!")


def get_application() -> FastAPI:
    app = FastAPI(
        title=config.PROJECT_NAME,
        version=config.PROJECT_VERSION,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=config.API_PREFIX)

    return app


app = get_application()
