from app.core.config import get_settings
from app.schemas.health import HealthResponse

class HealthService:
    async def get_health(self) -> HealthResponse:
        settings = get_settings()
        
        return HealthResponse(
            status="ok",
            version=settings.app_version,
        )
    
def get_health_service() -> HealthService:
    return HealthService()
