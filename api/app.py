from fastapi import FastAPI

from api.routers import health
from infrastructure.config import get_project_version
from infrastructure.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="SmartData Generator",
        description="Service IA de génération de données métier synthétiques.",
        version=get_project_version(),
    )

    app.include_router(health.router)

    return app


app = create_app()
