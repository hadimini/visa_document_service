from fastapi import FastAPI

from app.core import config


def get_application() -> FastAPI:
    app = FastAPI(
        title=config.PROJECT_NAME,
        version=config.PROJECT_VERSION,
    )

    return app

app = get_application()
