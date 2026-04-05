from fastapi import APIRouter, Depends

from app.schemas.health import HealthResponse
from app.services.health import HealthService, get_health_service

router = APIRouter()

@router.get("/service", response_model=HealthResponse)
async def health(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    return await service.get_health()