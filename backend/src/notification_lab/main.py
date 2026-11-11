from fastapi import FastAPI

from notification_lab.api.health import router as health_router

app = FastAPI(
    title="Distributed Notification Lab",
    description=(
        "A learning/demo system for simulated market and order events, "
        "asynchronous notification delivery, and failure observation."
    ),
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "name": "Distributed Notification Lab",
        "docs": "/docs",
        "health": "/health/live",
    }
