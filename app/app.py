from fastapi import FastAPI

from app.db.config import alchemy
from app.domains.users import routes as user_routes


def init_app() -> FastAPI:
    """
    Initialize the FastAPI application with database configuration.
    This function sets up the application and registers the database connection.
    """
    app = FastAPI(
        title="FastAPI Example",
        description="A simple FastAPI application example.",
        version="1.0.0",
    )

    # Add routers
    app.include_router(user_routes.router)

    # Other registrations
    alchemy.init_app(app=app)

    return app


app = init_app()
