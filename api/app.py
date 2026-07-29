from fastapi import FastAPI

from api.errors import register_exception_handlers
from api.routers import executions, health, schema_analysis
from infrastructure.config import get_project_version
from infrastructure.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="SmartData Generator",
        description="Service IA de génération de données métier synthétiques.",
        version=get_project_version(),
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(executions.router)
    app.include_router(schema_analysis.router)

    return app


app = create_app()
