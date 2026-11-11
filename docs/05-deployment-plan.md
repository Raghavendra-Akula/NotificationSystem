Distributed Notification Lab — Deployment Plan v0.1
1. Project goal
Build a public learning lab for a stock-broker-style notification system. The dashboard should show how price and order events move through services, how notifications are retried, and how queue backlog and latency change under load. This is a learning project, not a service for real trading customers.
2. Initial technology choices
- Backend services: Python; FastAPI for the REST API
- Dashboard: React
- Durable state: PostgreSQL
- Queue on GCP: Pub/Sub
- Containers: Docker
- Local orchestration: Docker Compose
- First cloud container platform: Cloud Run
- Push delivery in the first version: mock provider that can be configured to succeed, fail, or delay
- Observability: structured logs and metrics with eventId, notificationId, and traceId carried between services
3. Service responsibilities
- Dashboard: create test alerts, submit simulated events, and inspect notification timelines and system metrics.
- Notification API: accepts price-alert configuration and exposes notification status.
- Market simulator: emits ordered price updates for selected symbols.
- Order simulator: emits order execution updates such as PARTIALLY_FILLED and FILLED.
- Alert evaluator: consumes events, checks active alerts, and writes matching notification work.
- Outbox publisher: publishes committed notification work to the queue.
- Delivery worker: consumes notification work, calls the mock provider, and records attempts and status.
- PostgreSQL: stores alerts, market state, processed event IDs, notifications, delivery attempts, and outbox rows.
- Pub/Sub: buffers work between event processing and notification delivery.
4. Deployment stages
Stage A — Local lab
Run the dashboard, services, PostgreSQL, and Pub/Sub emulator with Docker Compose. Add controls in the dashboard to pause workers, inject provider failures, resend duplicate events, and generate bursts of price updates. Keep this as the main environment for repeatable experiments.
Stage B — Low-traffic public demo
Deploy the dashboard and stateless backend services as containers on Cloud Run, use Pub/Sub for queued work, and connect them to PostgreSQL. Set minimum instances to zero and set a conservative maximum instance count. Keep the mock push provider enabled.

For PostgreSQL, choose one of these explicitly:
1. Use the Cloud SQL trial for a temporary managed-database experiment; it is a 30-day trial, not an ongoing always-free database.
2. For an ongoing low-traffic demo, run PostgreSQL on a small Compute Engine VM. The free e2-micro allowance is limited to eligible US regions and includes up to 30 GB-months of standard disk and 1 GB/month of outbound transfer. This option needs database backups and careful memory limits.
Stage C — One-time scale experiment
Temporarily raise Cloud Run maximum instances and worker concurrency. Send a controlled load from a regional test client, observe queue backlog and latency, then stop the generator and return the service limits to their low-traffic settings. Delete temporary VMs and any temporary database resources after the run.
Stage D — Kubernetes learning exercise
First use local Kubernetes (such as kind or Minikube) to deploy the same containers. Create a short-lived GKE cluster only for learning managed Kubernetes behavior. GKE's monthly cluster credit covers the management fee for one eligible Autopilot or zonal cluster; workload compute is billed separately.
5. Geography and latency experiments
- Controlled simulation: add fixed delay and packet loss to a local load generator. Label results as simulated network conditions.
- Regional measurement: run temporary clients in GCP regions such as Mumbai, Europe, and the US, and call the same service endpoint. Label these as measured regional paths.
- Record API response latency separately from queue wait, worker processing, provider response, and app-observed delivery. A request header or a claimed client location does not create a real geographic network path.
6. Dashboard metrics
- Event and notification counts by status
- API request rate and p50/p95/p99 API latency
- Queue backlog and oldest-message age
- Worker instances, concurrency, and processing rate
- Retry count, provider failures, and dead-letter count
- Time from source event to notification queued and to provider response
- Regional probe latency, with simulated and measured results clearly distinguished
7. Cost and safety limits
- Local Docker Compose experiments should be the default for development and repeated load tests.
- Cloud Run and Pub/Sub have monthly free quotas, but usage beyond those quotas is billable.
- Cloud SQL is temporary free-trial capacity; budget for it or delete it before the trial ends.
- The free Compute Engine allowance is limited by region, disk, and outbound transfer. An in-use external IPv4 address is separately billed.
- Use a budget alert, cap Cloud Run maximum instances, avoid minimum instances, and delete temporary test resources. A budget alert notifies; it is not a hard spending cap.
- Do not send real trades, real account details, or real push tokens through the learning environment.
8. Scale-test scenarios
1. Normal flow: price crosses a threshold and creates one notification.
2. Duplicate delivery: replay the same event ID and verify no second logical notification appears.
3. Worker outage: pause workers, publish a burst, observe backlog growth, resume workers, and measure drain time.
4. Provider outage: make the mock provider fail, verify retry timing and final failure status.
5. Database slowdown: add controlled delay locally and observe the effect on event processing and queue backlog.
6. Regional latency: compare API and end-to-end processing measurements from each test location.
9. Completion criteria for the first public demo
- Dashboard is reachable through a public URL.
- A user can submit a simulated price or execution event and view its notification timeline.
- Duplicate events do not create duplicate logical notifications.
- Pausing and resuming workers visibly changes queue backlog.
- A simulated provider failure shows attempts, retry outcomes, and final status.
- Cloud deployment limits and resource cleanup steps are documented.