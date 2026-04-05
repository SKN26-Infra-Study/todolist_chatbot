from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings

def create_app() -> FastAPI():
    settings = get_settings()
    
    app = FastAPI(
        title="discord-todo-middle",
        version=settings.app_version
    )
    
    app.include_router(api_router,prefix="/api/v1")
    
    return app


app = create_app()