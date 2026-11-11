Distributed Notification Lab — Architecture v0.1
1. Purpose
This is a learning system for exploring asynchronous notification workflows, service boundaries, duplicate handling, retries, queue backlogs, scaling, and latency. It uses simulated stock and order events and a mock push provider. It does not place trades or send real broker notifications.
2. High-level architecture
Backend technology constraint
- Backend API: Python with FastAPI.
- API style: REST over HTTP with JSON request and response bodies.
- The alert evaluator, outbox publisher, and delivery worker are Python processes. They do not need to run as FastAPI servers unless they expose an operational or health-check endpoint.
- Other technology choices remain as listed in 05-deployment-plan.md and can be revised as the design develops.
flowchart TD
    UI["React dashboard"] --> API["Notification API"]
    API --> DB[("PostgreSQL")]
    SIM["Market and order simulators"] --> SOURCE["Source event topics"]
    SOURCE --> EVAL["Alert evaluator"]
    EVAL --> DB
    DB --> OUTBOX["Outbox publisher"]
    OUTBOX --> DELIVERY["Notification delivery topic"]
    DELIVERY --> WORKER["Delivery workers"]
    WORKER --> PROVIDER["Mock push provider"]
    WORKER --> DB
    API --> UI
The diagram shows the logical flow. Locally, Python services run as Docker containers and connect to PostgreSQL and a Pub/Sub emulator. In the GCP learning deployment, stateless services run as containers on Cloud Run, Pub/Sub carries asynchronous work, and PostgreSQL is hosted separately as described in 05-deployment-plan.md.
3. Components and responsibilities
Component	Responsibility
React dashboard	Create price alerts, submit or generate simulated events, inspect notification timelines and metrics, and control test scenarios such as pausing workers or injecting provider failures.
Notification API	Validate requests; create, list, and cancel price alerts; expose notification status and history. It does not wait for push delivery before responding.
Market simulator	Generate ordered price updates with a stable eventId, per-symbol sequence number, source timestamp, and symbol.
Order simulator	Generate execution updates such as PARTIALLY_FILLED and FILLED, with a stable event ID and order/execution identifiers.
Source event topics	Buffer market and execution events between producers and alert evaluation. Use separate market and execution topics or a shared topic with an explicit event type.
Alert evaluator	Consume source events, reject duplicate or stale events, match price threshold crossings, and create logical notifications.
PostgreSQL	Store alerts, latest market state, processed event IDs, notifications, delivery attempts, and the transactional outbox. It is the durable source of truth for the dashboard.
Outbox publisher	Find committed, unpublished outbox rows and publish notification work to the delivery topic. It marks rows published after the broker acknowledges publication.
Delivery workers	Consume notification work, call the mock push provider, record attempts, update notification status, and retry temporary errors with a limit.
Mock push provider	Simulate success, temporary failure, permanent failure, and response delay so the workflow can be tested without real device tokens.


4. End-to-end event flows
Price threshold alert
1. A user creates an ABOVE or BELOW alert through the dashboard. The API saves it as ACTIVE in PostgreSQL.
2. The market simulator publishes a price event containing eventId, symbol, price, sourceSequence, and occurredAt.
3. The alert evaluator consumes the event and starts a database transaction. A unique (source, eventId) key prevents the same event from being applied twice.
4. The evaluator locks or conditionally updates the saved market state for that symbol. It compares the previous price with the new price and ignores a stale sequence number.
5. For each crossing alert, it conditionally changes the alert from ACTIVE to FIRED. Only a successful state change creates a notification.
6. In the same transaction, it inserts the notification and an outbox row, then commits.
7. The outbox publisher sends the notification ID to the delivery topic. If it crashes after publishing but before marking the row, it may publish again; the delivery path must tolerate duplicate work.
8. A delivery worker calls the mock provider, records the result, and updates the notification status. The dashboard reads the persisted status and timeline through the API.
For the first price event for a symbol, save it as the baseline; do not treat it as a crossing because there is no prior price to compare.
Order execution notification
1. The order simulator publishes an execution event.
2. The evaluator inserts its event key. If it is new, it creates a notification and outbox row in one transaction.
3. The outbox and delivery flow is the same as for a price alert.
5. Status lifecycle
ACCEPTED → QUEUED → SENT_TO_PROVIDER
                    ↘ FAILED (after permanent error or retry limit)
SENT_TO_PROVIDER means the provider accepted the request. It does not prove that the mobile operating system displayed it. The MVP dashboard shows provider acceptance and mock results; a future mobile app can report app receipt or open events separately.
6. Reliability rules
- Event deduplication: use a unique source and event ID in PostgreSQL. A duplicate event becomes a no-op.
- Concurrent alert evaluation: update an alert only when its current state is ACTIVE; the database serializes conflicting updates to that row. Insert its notification in the same transaction as the state change.
- Notification idempotency: assign a stable notificationId and dedupeKey; consumers use these to recognize repeated delivery work.
- Transactional outbox: commit notification state and the work-to-publish record together. This prevents a committed notification from being lost because the process failed before publishing.
- Retries: retry temporary provider errors with bounded backoff. Send exhausted or permanent failures to a dead-letter path and show them in the dashboard.
- Delivery guarantee: the internal pipeline is at-least-once. Database constraints prevent duplicate logical notifications, but a provider timeout after it accepted a push can still make an external duplicate possible on retry.
7. Scaling model to experiment with
- Keep the API, evaluator, outbox publisher, and delivery workers stateless where possible; run more instances when a component is the bottleneck.
- The broker separates event intake from delivery. If events arrive faster than workers can process them, backlog and oldest-message age rise while producers can continue publishing within configured limits.
- Increase worker concurrency gradually and observe processing rate, database load, provider latency, and failure rate. More workers are not always better: they can overload PostgreSQL or the provider.
- Scale the evaluator and delivery workers independently because their workloads and bottlenecks differ.
- Begin with one database and one region. Measure before introducing partitioning, replicas, or multiple regions.
8. Observability and geography
Carry eventId, notificationId, and traceId across API calls, broker messages, database records, and worker logs. Record timestamps for event creation, API acceptance, event processing, queue publication, worker start, provider response, and app callback when available.

Show these separately in the dashboard:
- API request latency and request rate
- Event-to-evaluator delay
- Outbox publication delay
- Delivery queue delay and backlog
- Worker processing time and provider response time
- End-to-end time to provider acceptance
For geography, use load generators deployed in real GCP regions and call the same public endpoint. Record the generator region with each measurement. Artificial delay or packet loss is a separate simulation and must be labeled as simulated; a location field in a request does not create a regional network path.
9. Interview concepts this architecture demonstrates
Transactional outbox, at-least-once delivery, idempotent consumers, unique constraints, row-level locking, event ordering, backpressure, queue-based decoupling, bounded retries, dead-letter handling, independent service scaling, observability, and regional latency measurement.