from fastapi import FastAPI

from api.errors import register_exception_handlers
from api.routers import data_import, documents, executions, health, projects, schema_analysis
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
    app.include_router(projects.router)
    app.include_router(documents.router)
    app.include_router(data_import.router)

    return app


app = create_app()
