from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create the tables in the database if they don't exist
    print("Server is starting...")
    await init_db()
    yield
    print("Server has been stopped...")


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

    return app

app = get_application()
