Price update
  → Price event received
  → Check whether this event was already processed
  → Find active alerts for the symbol
  → If a threshold was crossed, record the alert firing and create a notification
  → A worker sends the push notification
  → Dashboard shows the resulting status

Order execution update
  → Execution event received
  → Check whether this event was already processed
  → Create a notification for the user
  → A worker sends the push notification
  → Dashboard shows the resulting status

Duplicate source events: store processed IDs with a uniqueness constraint. If a ID is seen again skip processing it.

Price alert fires once: Mark the alert as fired in the same database transaction that creates its notification. This prevents two workers from creating two logical notifications for the same one-shot alert.

Atomic recording: Save the event’s processed status, alert state, notification, and outgoing work together. If the transaction fails, none of those changes should be left half-complete.

Retries: Retry temporary push-provider failures with a limit. Record persistent failures for inspection instead of retrying forever.

Late price events: Include the source timestamp and, for the simulator, a sequence number per symbol. Ignore and record updates older than the last processed sequence. Later, we can examine more advanced ordering and recovery strategies.
Delivery status: Track ACCEPTED, QUEUED, SENT_TO_PROVIDER, and FAILED. A provider accepting a push does not prove the phone displayed it.