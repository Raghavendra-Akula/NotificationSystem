# Trading Alert Service — Requirements v0.1

## 1. Problem
Notify users when a stock price crosses an alert threshold or their order execution changes.

## 2. Users and use cases
- A user creates, views, and cancels a price alert.
- A user receives a mobile notification when the alert condition is met.
- A user receives a notification when an order is partially filled or filled.
- An admin views notification status and timing in a dashboard.

## 3. Scope
### MVP includes
- Price threshold alerts
- Simulated market price events
- Simulated order execution events
- Mobile push notification delivery
- Notification history and status dashboard

### Out of scope for MVP
- Placing or changing trades
- Connecting to a real broker or market-data provider
- Multiple regions
- Scheduled notifications - need to think about it later.

## 4. Business rules
- A price alert fires when the price crosses its threshold.
- A price alert fires only once unless the user rearms it.
- Reprocessing the same source event must not create a second logical notification.
- The system records whether a notification was accepted, queued, sent to the provider, or failed.
- “Sent to provider” does not necessarily mean the phone displayed the notification.

## 5. Events
### Price update
Fields: event ID, symbol, price, observed time.

### Order execution update
Fields: event ID, user ID, order ID, symbol, execution status, quantity, price, event time.

## 6. Reliability and correctness
- How will duplicate events be identified?
- What should happen if events arrive late or out of order?
- How many delivery attempts should be made after a temporary failure? 
--> user should get atleast one notification here in this case of failure.
- What should happen to an event that keeps failing?
--> after retrying 5 times email should be send to user mentioning please create new notification this is removed from queue.

## 7. Initial scale and latency targets
- Expected users: TBD
- Active price alerts: TBD
- Peak incoming price events per second: TBD
- Peak notification events per second: TBD
- API response target: TBD
- Price-event-to-queued-notification target: TBD
- Regions used for measurement: TBD

## 8. MVP acceptance criteria
- Creating an alert makes it visible in the dashboard.
- A simulated threshold crossing creates one notification.
- Replaying the same event does not create a duplicate logical notification.
- A simulated order fill creates a notification.
- A delivery failure appears in the dashboard with its status and attempt count.