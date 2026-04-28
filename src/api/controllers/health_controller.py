from fastapi import APIRouter, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from src.infrastructure.persistence.db_context import check_database_health

router = APIRouter()

REQUEST_COUNTER = Counter("api_health_checks_total", "Total health checks", ["endpoint"])
READINESS_LATENCY = Histogram(
    "api_readiness_check_duration_seconds",
    "Readiness latency in seconds",
)


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness() -> dict[str, str]:
    REQUEST_COUNTER.labels(endpoint="liveness").inc()
    return {"status": "alive"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness() -> dict[str, str]:
    REQUEST_COUNTER.labels(endpoint="readiness").inc()
    with READINESS_LATENCY.time():
        db_ok = check_database_health()
    if not db_ok:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return {"status": "ready"}


@router.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
