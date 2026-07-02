from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from core.context import get_db_session
from api.deps import logger

api_healthcheck = APIRouter()


class HealthStatus:
    """Health status response model."""
    
    def __init__(self, status: str, database: str = None, message: str = None):
        self.status = status
        self.database = database or "unknown"
        self.message = message or "OK"
    
    def dict(self):
        return {
            "status": self.status,
            "database": self.database,
            "message": self.message,
        }


@api_healthcheck.get(
    "/",
    response_model=dict,
    status_code=HTTPStatus.OK,
    summary="Health check",
    description="Check service health and basic connectivity.",
)
async def health_check():
    """Simple health check.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy", "message": "Service is running"}


@api_healthcheck.get(
    "/ready",
    response_model=dict,
    status_code=HTTPStatus.OK,
    summary="Readiness probe",
    description="Check if service is ready to accept requests (database connectivity check).",
)
async def readiness_check():
    """Readiness probe - checks database connectivity.
    
    Returns:
        dict: Readiness status with database connectivity info
        
    Raises:
        HTTPException: 503 if database is unreachable
    """
    try:
        db_session = get_db_session()
        await db_session.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "database": "connected",
            "message": "Service is ready to accept requests",
        }
    except Exception as e:
        logger.error(f"Database connectivity check failed: {e}")
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Database is unreachable. Service is not ready.",
        )


@api_healthcheck.get(
    "/live",
    response_model=dict,
    status_code=HTTPStatus.OK,
    summary="Liveness probe",
    description="Check if service is alive (for Kubernetes liveness probes).",
)
async def liveness_check():
    """Liveness probe - checks if service process is running.
    
    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "message": "Service process is running",
    }
