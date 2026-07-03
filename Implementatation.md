
# 🗺️ Feature Map & Learning Blueprint

> This document defines **what** you're building, **why** it matters, and **how to think** about each feature before touching code.

---

## 🏛️ Architecture Philosophy

You are building a **modular monolith** — not microservices, not a spaghetti app.

**Modular monolith** means:

- Single deployable unit (one FastAPI app)
- Internally divided into **cohesive modules** with clear boundaries
- Modules communicate through **service interfaces**, not direct imports across layers
- When the time comes to extract a microservice, the module boundary is already clean

```
You will feel the discipline of this in Week 1.
You will appreciate it in Week 4.
You will be grateful for it in Week 6.
```

---

## 📦 Module Overview

```
ride-sharing-backend/
│
├── auth/           → Identity, JWT, RBAC
├── users/          → User profiles, roles
├── rides/          → Ride lifecycle, booking, status
├── matching/       → Route overlap, companion matching
├── fare/           → Dynamic pricing, fare splitting
├── drivers/        → Driver management, approval flow
├── notifications/  → Event-driven alerts (Kafka consumer)
└── shared/         → Cross-cutting: DB, Redis, Kafka, exceptions
```

Each module owns its **models, schemas, repository, service, and router**. Nothing leaks across module boundaries except through explicit service calls.

---

## 🔐 Feature 1: Authentication & Authorization (RBAC)

### What You're Building

|Endpoint|Method|Description|
|---|---|---|
|`/auth/register`|POST|Create rider/driver account|
|`/auth/login`|POST|Return JWT access + refresh token|
|`/auth/logout`|POST|Invalidate refresh token via Redis blocklist|
|`/auth/refresh`|POST|Exchange refresh token for new access token|
|`/users/me`|GET|Return authenticated user profile|
|`/users/me`|PATCH|Update own profile|

### Roles in the System

```
RIDER   → can book rides, request companions, split fares
DRIVER  → can accept/reject rides, confirm pickups, update ride status
ADMIN   → can view all data, manage users, override fares
```

### Prerequisites Before You Build This

- Docker Compose running (PostgreSQL + Redis + FastAPI)
- `pydantic-settings` configured for environment variables
- SQLAlchemy async engine initialized
- Alembic configured and first migration ready to run

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**Layered Architecture**|auth router → auth service → user repository|Keeps HTTP concerns out of business logic|
|**Repository Pattern**|`UserRepository` — all SQL lives here|Testable, swappable, no raw queries in services|
|**DTO Pattern**|`RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`|Never expose ORM models directly|
|**Dependency Injection**|`get_current_user`, `require_role(...)`|Composable, testable auth guards|
|**Factory Pattern**|`create_access_token()`, `create_refresh_token()`|Centralized token construction|

### Concepts You Must Learn While Building This

**JWT Deep Dive**

- Structure: `header.payload.signature` — decode one manually in jwt.io
- Why stateless auth is powerful AND dangerous
- Access token (short-lived, 15min) vs refresh token (long-lived, 7 days)
- Why you cannot revoke a JWT without a blocklist — and how Redis solves this

**Password Security**

- Why you never store plaintext passwords (obvious) but also why MD5/SHA1 are wrong
- `bcrypt` work factor — what it means for performance at scale
- `passlib` as the abstraction layer

**RBAC vs ABAC**

- Role-Based: "Drivers can accept rides" → simple, what you're building
- Attribute-Based: "Drivers can accept rides in their city" → more granular, stretch goal
- Why RBAC is the right starting point for most systems

**Token Refresh Flow**

- Why refresh tokens exist (security vs UX tradeoff)
- Rotation strategy: each refresh issues a new refresh token and invalidates the old one
- Redis as the revocation store — `SET token_jti "revoked" EX 604800`

**Request/Response Lifecycle in FastAPI**

```
Incoming HTTP Request
        ↓
Middleware stack (CORS, logging, timing)
        ↓
Router matching
        ↓
Dependency resolution (get_db, get_current_user)
        ↓
Endpoint function executes
        ↓
Pydantic response_model serializes output
        ↓
HTTP Response sent
```

Draw this. Know exactly where errors can occur at each stage.

**Serialization vs Deserialization**

- Deserialization: JSON bytes → Pydantic model (input validation happens here)
- Serialization: Python object → JSON bytes (response_model controls what leaves)
- The **DTO pattern** means your internal User ORM object never directly becomes JSON — a `UserResponse` Pydantic model controls exactly what fields are exposed

---

## 🚗 Feature 2: Ride Booking & Lifecycle

### What You're Building

|Endpoint|Method|Description|
|---|---|---|
|`/rides`|POST|Book a new ride|
|`/rides/{ride_id}`|GET|Get ride details|
|`/rides`|GET|List my rides (paginated)|
|`/rides/{ride_id}/cancel`|POST|Cancel a ride|
|`/rides/{ride_id}/status`|PATCH|Driver updates ride status|

### Ride State Machine

```
REQUESTED
    ↓
DRIVER_ASSIGNED
    ↓
DRIVER_ARRIVING
    ↓
IN_PROGRESS
    ↓
COMPLETED / CANCELLED
```

Every status transition is validated. You cannot jump from `REQUESTED` to `COMPLETED`. Invalid transitions return `422 Unprocessable Entity` with a descriptive error.

### Prerequisites Before You Build This

- Auth module complete (`get_current_user` working)
- User roles enforced (`require_role(Role.RIDER)`)
- Alembic migrations workflow understood
- Layered architecture established (router → service → repository)

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**State Machine Pattern**|`RideService.transition_status()`|Prevents illegal state transitions|
|**Repository Pattern**|`RideRepository`|All ride queries in one place|
|**Idempotency Key Pattern**|`POST /rides` with `Idempotency-Key` header|Prevent duplicate ride bookings on retry|
|**Unit of Work**|Ride creation + fare record in one transaction|Atomicity — both created or neither|
|**Optimistic Locking**|Ride status updates|Prevent race conditions when driver and system update simultaneously|

### Concepts You Must Learn While Building This

**Idempotency in API Design**

- What happens when a client times out and retries `POST /rides`?
- The idempotency key: client sends `Idempotency-Key: uuid` header
- Server checks Redis/DB: "Have I seen this key before?"
- If yes → return cached response. If no → process and store result.
- This is **not optional** in production payment and booking systems

**Database Transactions & ACID**

- Atomicity: ride creation and initial fare record happen together or not at all
- Why `async with session.begin()` matters — understand what happens if your service raises halfway through
- Isolation levels: what "read committed" means and when you need "serializable"

**Optimistic vs Pessimistic Locking**

- Pessimistic: `SELECT FOR UPDATE` — lock the row, nobody else touches it
- Optimistic: add a `version` column, check it on update, retry if conflict
- For ride status updates: optimistic locking is right (conflicts are rare but must be handled)

**Pagination, Filtering, Sorting**

- Never return unlimited records from `GET /rides`
- Cursor-based pagination vs offset pagination — understand the tradeoff
- Offset breaks under concurrent inserts; cursor is production-safe
- `GET /rides?status=COMPLETED&sort=created_at&order=desc&limit=20&cursor=xxx`

**SQLAlchemy Async Patterns**

- `AsyncSession` vs `Session` — why async matters for FastAPI
- Lazy loading is dangerous with async — always use `selectinload` or `joinedload`
- The N+1 query problem — how to detect and prevent it

---

## 👥 Feature 3: Ride Companion Matching

### What You're Building

|Endpoint|Method|Description|
|---|---|---|
|`/rides/{ride_id}/companion-request`|POST|Opt into ride sharing|
|`/rides/available-companions`|GET|Find compatible rides to join|
|`/rides/{ride_id}/companions/{companion_id}/approve`|POST|Driver approves companion|
|`/rides/{ride_id}/companions/{companion_id}/reject`|POST|Driver rejects companion|

### Route Matching Logic

```
Primary rider:   Chennai Central → Potheri
Companion rider: Tambaram       → Potheri

Matching criteria:
  1. Same destination (or destination within N km radius)
  2. Companion pickup point is along the primary route
  3. Ride is in REQUESTED or DRIVER_ASSIGNED state
  4. Primary rider opted into companion sharing
  5. Driver has not yet rejected companion requests
```

### Prerequisites Before You Build This

- Ride booking complete and tested
- Ride state machine working
- Auth and RBAC enforced on all endpoints
- Basic fare calculation logic present (Feature 4)

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**Strategy Pattern**|Route matching algorithm|Swap simple distance matching for ML-based matching later|
|**Repository Pattern**|`CompanionRequestRepository`|Query companion requests by status, ride, user|
|**Cache-Aside Pattern**|Available companions list|Expensive geo query — cache results for 30 seconds|
|**Outbox Pattern**|Companion match found → Kafka event|Reliable event publishing without dual-write problem|

### Concepts You Must Learn While Building This

**Geospatial Basics for Backend Engineers**

- Latitude/longitude as coordinates — why you cannot use simple subtraction for distance
- Haversine formula: great-circle distance between two points
- PostGIS extension: `ST_DWithin`, `ST_Contains` — production geo queries
- For learning: implement Haversine in Python first, then understand why PostGIS is better at scale

**The Dual-Write Problem**

- You want to: update DB (companion matched) AND publish Kafka event
- If DB succeeds but Kafka fails → inconsistent state
- If Kafka succeeds but DB fails → phantom event
- The **Outbox Pattern** solves this:

    ```
    1. Write companion_match to DB
    2. Write event to outbox table in SAME transaction
    3. Background worker reads outbox and publishes to Kafka
    4. Mark outbox record as published
    ```

    Only one write boundary → no dual-write problem

**Cache-Aside Pattern**

python

```
result = await redis.get(cache_key)
if result:
    return deserialize(result)
result = await repository.find_available_companions(...)
await redis.setex(cache_key, 30, serialize(result))
return result
```

- When to cache: expensive queries, frequently read, tolerate slight staleness
- When NOT to cache: financial data, ride status (must be real-time)
- Cache invalidation: the second hardest problem in CS — invalidate on companion approval/rejection

**Eventual Consistency Thinking**

- When a companion is approved, multiple things need to happen:
    - Companion record updated in DB
    - Both riders notified
    - Fare recalculated
    - Driver app updated
- These don't all happen atomically — they happen **eventually** via events
- Your system must be correct even if some events are delayed or arrive out of order

---

## 💰 Feature 4: Dynamic Fare & Cost Splitting

### What You're Building

|Endpoint|Method|Description|
|---|---|---|
|`/rides/{ride_id}/fare`|GET|Get current fare estimate|
|`/rides/{ride_id}/fare/recalculate`|POST|Trigger recalculation on companion join|
|`/rides/{ride_id}/fare/split`|GET|Get each rider's share breakdown|

### Fare Calculation Model

```
Base fare components:
  - Base rate: ₹50 flat
  - Per km rate: ₹12/km
  - Per minute rate: ₹2/min
  - Surge multiplier: 1.0x–3.0x (time + demand based)

Single rider:
  total_fare = (base + distance_fare + time_fare) * surge

Shared ride (companion joins at Tambaram):
  primary_distance   = Chennai Central → Potheri (full route)
  companion_distance = Tambaram → Potheri (partial route)
  shared_segment     = Tambaram → Potheri (overlap)

  shared_segment_cost = shared_segment_fare * surge

  primary_pays   = solo_segment_fare + (shared_segment_cost * 0.55)
  companion_pays = shared_segment_cost * 0.45

  Both pay less than solo fare → incentive to share
```

### Prerequisites Before You Build This

- Ride booking working
- Companion matching implemented
- Ride location tracking (start/pickup points stored)
- Kafka infrastructure running

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**Strategy Pattern**|`FareCalculationStrategy`|Swap algorithms (simple distance, ML surge, per-segment)|
|**Event-Driven Architecture**|`CompanionJoined` event → fare recalculation|Decoupled, the fare service doesn't need to know about matching internals|
|**Saga Pattern (simplified)**|Fare recalculate → notify riders → update payment intent|Multi-step process that must be compensatable|
|**Immutable Fare Records**|Append-only fare history|Audit trail — never UPDATE a fare record, INSERT a new version|

### Concepts You Must Learn While Building This

**Event-Driven Architecture Fundamentals**

- Producer: matching service publishes `CompanionJoinedEvent` to Kafka topic `ride.companion.joined`
- Consumer: fare service subscribes to that topic, recalculates fare
- Why this is better than direct service calls: decoupled, retryable, auditable

**Event Schema Design**

python

```
class CompanionJoinedEvent(BaseModel):
    event_id: UUID          # for idempotency
    event_type: str         # "companion.joined"
    event_version: str      # "1.0" — schema evolution
    ride_id: UUID
    companion_rider_id: UUID
    pickup_location: Coordinates
    timestamp: datetime
```

- Always include `event_id` for deduplication
- Always include `event_version` for schema evolution
- Events are **facts** — past tense, immutable

**Consumer Idempotency**

- Kafka guarantees **at-least-once delivery** — your consumer will see duplicates
- Every consumer must check: "Have I processed `event_id` X before?"
- Store processed `event_id` values in Redis with TTL or in a DB table
- This is not optional — it's what separates production systems from demos

**Dead Letter Queue (DLQ) Concept**

- What happens when fare recalculation fails 3 times in a row?
- DLQ: failed messages go to a separate topic `ride.companion.joined.dlq`
- Ops team can inspect, fix the bug, and replay messages
- Without DLQ: silent failure, riders never get recalculated fare

**Transactional Integrity in Fare Updates**

- Fare recalculation must be atomic: new fare record + both riders' share records
- If the Kafka consumer crashes halfway through: idempotency key prevents double-processing on retry
- Saga pattern: if fare recalculation fails, emit a compensating event

---

## 🔔 Feature 5: Notifications & Real-Time Updates

### What You're Building

|Channel|Trigger|Recipient|
|---|---|---|
|Kafka consumer → push|Driver assigned|Rider|
|Kafka consumer → push|Companion approved|Both riders|
|Kafka consumer → push|Fare recalculated|Both riders|
|Kafka consumer → push|Ride status changed|All parties|
|WebSocket (stretch)|Real-time driver location|Rider|

### Prerequisites Before You Build This

- Kafka infrastructure running
- Events being published from matching and fare services
- Rider and driver device tokens stored in user profile

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**Event-Driven Architecture**|All notifications triggered by Kafka events|Notifications are side effects, not primary flow|
|**Dead Letter Queue**|Failed notification attempts|Don't lose notifications silently|
|**Retry Pattern**|Push notification failures|Network blips shouldn't mean missed alerts|
|**Consumer Group Pattern**|Notification service as its own consumer group|Independent from fare service consumption|

### Concepts You Must Learn While Building This

**Kafka Consumer Groups**

- Multiple services can consume the same event independently
- `fare-service` consumer group and `notification-service` consumer group both consume `ride.companion.joined`
- Each group maintains its own offset — they don't interfere
- This is the **fan-out** pattern in event-driven systems

**Retry Pattern with Exponential Backoff**

```
Attempt 1: immediate
Attempt 2: wait 1s
Attempt 3: wait 2s
Attempt 4: wait 4s
Attempt 5: → DLQ
```

- Why exponential? Prevent thundering herd on downstream recovery
- Why a maximum? Don't retry forever — acknowledge failure and alert

**Background Task Processing**

- FastAPI `BackgroundTasks` for lightweight fire-and-forget (logging, simple notifications)
- Celery or Kafka consumer for reliable, retryable background work
- Know the difference: `BackgroundTasks` is in-process and dies with the request worker

---

## 📊 Feature 6: Observability & Production Readiness

### What You're Building

|Component|What|
|---|---|
|Structured logging|JSON logs with trace_id, user_id, ride_id, duration|
|Health checks|`/health` with DB + Redis + Kafka connectivity|
|Request tracing|Correlation IDs propagated across service calls|
|Exception handling|Global handler, consistent error envelope|
|Metrics (stretch)|Prometheus endpoint, request count/latency|

### Design Patterns to Apply

|Pattern|Where|Why|
|---|---|---|
|**Correlation ID Pattern**|Middleware injects `X-Request-ID` into all logs|Trace a single request across all log lines|
|**Health Check Pattern**|`/health/live` + `/health/ready`|Kubernetes-style liveness vs readiness probes|
|**Structured Logging**|Every log line is JSON|Machine-parseable, queryable in ELK/Datadog|

### Concepts You Must Learn While Building This

**Why Observability is a First-Class Concern**

- In production, you cannot attach a debugger
- Logs, metrics, and traces are your only window into a running system
- Build observability from Week 1, not as an afterthought

**Structured Logging vs Print Statements**

python

```
# Bad (unstructured)
print(f"User {user_id} booked ride {ride_id}")

# Good (structured)
logger.info("ride.booked", extra={
    "user_id": str(user_id),
    "ride_id": str(ride_id),
    "trace_id": ctx.trace_id,
    "duration_ms": elapsed
})
```

**The Three Pillars of Observability**

- **Logs**: What happened (events, errors, state changes)
- **Metrics**: How much / how fast (request rate, latency p99, error rate)
- **Traces**: Where did time go (distributed request tracing)

---

## 🧪 Testing Strategy

### Testing Pyramid for This Project

```
          /\
         /  \
        / E2E \          ← Few: full flow tests (book → match → fare)
       /--------\
      / Integration\     ← Some: service + DB + Redis tests
     /--------------\
    /   Unit Tests   \   ← Many: service logic, fare calculation, state machine
   /------------------\
```

|Layer|What to Test|Tools|
|---|---|---|
|Unit|Fare calculation, state machine transitions, route matching math|`pytest`, no DB|
|Integration|Repository queries, Kafka publish/consume|`pytest` + test DB|
|API|Full request/response cycle|`TestClient`, `httpx`|
|Contract|Event schema compatibility|`pydantic` schema validation|

---

## 🚨 Common Mistakes to Avoid (Global)

|Mistake|Consequence|Correct Approach|
|---|---|---|
|Exposing ORM models as responses|Leaks internal fields, breaks on schema change|Always use Pydantic response schemas|
|No idempotency on booking|Duplicate rides on client retry|Idempotency-Key header + Redis check|
|Sync SQLAlchemy in async FastAPI|Thread blocking, poor performance|Use `AsyncSession` throughout|
|No state machine validation|Rides jump to invalid states|Explicit transition matrix|
|Publishing Kafka events outside transaction|Dual-write inconsistency|Outbox pattern|
|Caching fare data|Riders see stale prices|Never cache financial data|
|No DLQ for consumers|Silent failures, lost events|Always configure DLQ|
|Global mutable state|Race conditions, test pollution|Dependency injection for all state|
|N+1 queries in ride listing|Database overload|Use `selectinload` / `joinedload`|
|Logging secrets|Security breach|Sanitize all log output|
