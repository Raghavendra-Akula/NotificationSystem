| Table | Purpose | Key constraint or index |
|---|---|---|
| `price_alerts` | User, symbol, threshold, direction, and state (`ACTIVE`, `FIRED`, `CANCELLED`) | Index on `(symbol, state)` |
| `processed_events` | Remembers which market or execution events were handled | Unique `(source, event_id)` |
| `notifications` | Stores the user-facing notification and its status | Unique `dedupe_key` |
| `device_tokens` | Maps users to mobile push tokens | Unique token |
| `delivery_attempts` | Records each push attempt and its result | Unique `(notification_id, attempt_number)` |
| `outbox` | Stores work that must be published for delivery | Track whether each entry has been published |


The important part is to document three separate safeguards:
1. Same event delivered twice: processed_events has a unique (source, event_id) key. If two workers receive the same event, only one can record it as new; the other skips it.
2. Different price events race to fire one alert: both may have different event IDs, so event deduplication alone won’t stop them. In a database transaction, update the alert from ACTIVE to FIRED only if it is still ACTIVE. Only the worker whose update succeeds creates the notification.
3. Final duplicate guard: give the notification a unique dedupe_key. For a one-shot price alert, use a key based on the alert ID. For an execution update, use the execution event ID.

For each event document the transaction order
Begin transaction
  → Record the event as processed
  → If it is new, update the alert or create the execution notification
  → Create the notification and outbox entry
Commit
Acknowledge the broker event

If recording any part fails, the transaction rolls back, so the event can be retried without leaving a partially created notification. The push worker reads the outbox work after commit.