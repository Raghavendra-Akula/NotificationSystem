# Distributed Notification Lab

A local learning project for understanding how distributed services process simulated stock-price and order-execution events, create notifications, retry delivery, and expose status and timing. This is a demo only: it does not place trades, connect to broker accounts, or send real push notifications.

## Technology

- Python and FastAPI REST API
- PostgreSQL for durable state (to be added)
- Google Cloud Pub/Sub, with the Pub/Sub emulator locally (to be added)
- Docker and Docker Compose (to be added)
- React dashboard (to be added)
- Configurable mock push provider (to be added)

See the docs directory for requirements, event contracts, data model, architecture, deployment plan, and API contract.

## Run the current API skeleton

The project uses Python 3.11 or newer. Python 3.12 is recommended.

From the repository root, create and activate a virtual environment:

    python3.12 -m venv .venv
    source .venv/bin/activate

Install the backend package and dependencies:

    python -m pip install --upgrade pip
    python -m pip install -e ./backend

Start the development server:

    uvicorn notification_lab.main:app --app-dir backend/src --reload

Open http://127.0.0.1:8000/docs for the interactive API documentation.

## Check the running application

In another terminal, from the repository root:

    curl -i http://127.0.0.1:8000/health/live
    curl -i http://127.0.0.1:8000/health/ready

The liveness endpoint should return 200 with {"status":"ok"}. Readiness currently returns 503 and reports PostgreSQL and the event transport as not_configured; that is expected until those dependencies are implemented. The root endpoint is at http://127.0.0.1:8000/.

To stop the server, press Ctrl+C. To leave the virtual environment, run deactivate.

## Open in Visual Studio Code

Open this repository folder in Visual Studio Code. Its built-in Git source control detects the initialized .git repository. The workspace settings select .venv/bin/python as the interpreter, and the recommended Python extension provides Python editor support.

## Current scaffold scope

The first stage includes the FastAPI app, health endpoints, Python package metadata, local virtual environment instructions, and Git/VS Code settings. It does not yet connect to PostgreSQL or Pub/Sub. Alert CRUD, simulated event ingestion, event processing, the transactional outbox, delivery workers, dashboard, and Docker Compose are subsequent stages.

## Learning sequence

1. Repository structure and FastAPI application skeleton.
2. PostgreSQL schema and migrations.
3. Alert creation and simulated event submission.
4. Event processing, deduplication, ordering, and atomic alert firing.
5. Transactional outbox and Pub/Sub integration.
6. Delivery worker, mock provider, retries, and dead-letter handling.
7. Dashboard and notification timeline.
8. Docker Compose local environment.
9. Metrics and controlled load tests.
10. Cost review, then low-traffic GCP deployment and real regional probes.
11. Short-lived Kubernetes/GKE learning experiment.

Do not create billable cloud resources or deploy publicly before reviewing the cost and deployment plan. Keep real broker credentials, accounts, and push tokens out of this learning environment.
