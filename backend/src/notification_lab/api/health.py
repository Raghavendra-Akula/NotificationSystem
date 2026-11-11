from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Check whether the API process is running")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", summary="Check whether the API can serve requests")
def readiness() -> JSONResponse:
    # PostgreSQL and Pub/Sub are not wired in the skeleton yet. Report this
    # honestly so a deployment does not mistake an incomplete app for ready.
    body = {
        "status": "not_ready",
        "checks": {
            "postgres": "not_configured",
            "eventTransport": "not_configured",
        },
    }
    return JSONResponse(status_code=503, content=body)
