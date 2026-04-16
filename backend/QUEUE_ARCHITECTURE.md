# Queue System Architecture — Celery + Redis

Reference: [Issue #25 — Queue System](https://github.com/FCTE-UNB-EPS5/buscador-osint-automatizado-eps_2026_1_grupo_1/issues/25)

---

## Overview

The queue system is a decoupled module that powers all asynchronous operations in the Buscador OSINT backend: scraper task dispatch, result collection, retry logic, dead letter queue management, and monitoring. It is built on **Celery 5.4+** with **Redis 7** as both broker and result backend.

```
┌─────────────┐     ┌───────────┐     ┌──────────────────┐
│  FastAPI     │────>│  Celery   │────>│  Redis 7         │
│  (dispatch)  │     │  Worker   │     │  (broker +        │
│              │     │           │     │   result backend) │
└─────────────┘     └─────┬─────┘     └──────────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         ┌────▼───┐  ┌───▼────┐  ┌───▼──────┐
         │scrapers│  │evidence│  │  default  │
         │ queue  │  │ queue  │  │  queue    │
         └────────┘  └────────┘  └──────────┘
                          │
                    ┌─────▼─────┐
                    │dead_letter│
                    │  queue    │
                    └───────────┘
```

## Module Structure

```
backend/src/
├── core/
│   ├── config.py          # Pydantic Settings (RedisSettings, CelerySettings)
│   └── celery_app.py      # Celery instance, broker config, task routes
└── queue/
    ├── retry.py           # Exponential backoff policy
    ├── base_task.py       # BaseScraperTask with retry, audit logging, DLQ hooks
    ├── dlq.py             # DLQManager — send, list, replay, purge
    ├── router.py          # FastAPI admin endpoints for DLQ
    ├── health.py          # Redis health check + queue depth probes
    ├── monitoring.py      # Prometheus metrics (queue depth, throughput, failures)
    └── beat_schedules.py  # Periodic tasks (health check, data retention purge)
```

The `queue/` package is intentionally self-contained. All inter-module dependencies flow inward (core -> queue), making it straightforward to extract or test independently.

---

## Components

### Configuration (`core/config.py`)

Two Pydantic Settings classes load all configuration from environment variables:

| Class | Env prefix | Key fields |
|---|---|---|
| `RedisSettings` | `REDIS_` | `host`, `port`, `db`, `password`, `max_memory` |
| `CelerySettings` | `CELERY_` | `broker_url`, `result_backend`, `task_serializer`, `accept_content` |

No secrets are hardcoded. The `RedisSettings.url` property builds the connection string dynamically.

### Celery Application (`core/celery_app.py`)

- App name: `buscador_osint`
- Serialization: **JSON only** (`task_serializer`, `result_serializer`, `accept_content` are all `json`). Pickle is explicitly excluded for security (Bandit B301).
- Task routing:
  - `src.queue.*scraper*` -> `scrapers` queue
  - `src.queue.*evidence*` -> `evidence` queue
  - Everything else -> `default` queue
- Auto-discovers tasks in `src.queue`

### Retry Policy (`queue/retry.py`)

Exponential backoff as specified in Issue #25:

| Retry # | Delay |
|---|---|
| 1st | 60 seconds |
| 2nd | 300 seconds (5 min) |
| 3rd | 900 seconds (15 min) |

After 3 retries the task is marked as failed and sent to the dead letter queue. The `get_retry_delay(retries)` function clamps to the last value for any retry beyond the list length.

### Base Scraper Task (`queue/base_task.py`)

`BaseScraperTask` extends `celery.Task` and provides:

- **`max_retries = 3`** with `acks_late = True` for at-least-once delivery
- **`before_start`** — structured log with task name, ID, args, and timestamp (audit trail)
- **`after_return`** — structured log with status and elapsed time
- **`on_retry`** — warning log with retry count and exception
- **`on_failure`** — error log; flags when retries are exhausted
- **`retry_with_backoff(exc)`** — convenience method that applies the exponential backoff delay

All scraper tasks should inherit from `BaseScraperTask`:

```python
@app.task(base=BaseScraperTask, bind=True, name="src.queue.portal_scraper")
def portal_scraper(self, query: str):
    try:
        return scrape_portal(query)
    except TransientError as exc:
        self.retry_with_backoff(exc=exc)
```

### Dead Letter Queue (`queue/dlq.py`)

`DLQManager` stores failed tasks in a Redis list (`dead_letter` key):

| Method | Description |
|---|---|
| `send_to_dlq(task_name, task_id, args, kwargs, exception)` | Write a failed task entry; returns the DLQ entry ID |
| `list_dlq(limit, offset)` | Paginated retrieval of DLQ entries |
| `get_entry(entry_id)` | Lookup a specific entry by ID |
| `replay_task(entry_id, celery_app)` | Re-dispatch the task and remove from DLQ |
| `purge()` | Delete all DLQ entries |
| `count()` | Number of entries in the DLQ |

Each DLQ entry stores: `id`, `task_name`, `task_id`, `args`, `kwargs`, `exception` (message only, no tracebacks — LGPD consideration), and `timestamp`.

### DLQ Admin Endpoints (`queue/router.py`)

FastAPI router mounted at `/api/admin/dlq`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/dlq` | List entries (paginated: `?limit=100&offset=0`) |
| `POST` | `/api/admin/dlq/{entry_id}/replay` | Replay a specific failed task |
| `DELETE` | `/api/admin/dlq` | Purge all entries |

### Health Checks (`queue/health.py`)

- **`check_redis_health(client)`** — Runs `PING`, queries `INFO memory` and `INFO server`. Returns `{"status": "healthy/unhealthy", "memory_used", "memory_peak", "uptime_seconds"}`.
- **`check_queue_depths(client)`** — Returns `LLEN` for each queue: `default`, `scrapers`, `evidence`, `dead_letter`. Returns `-1` on error.

### Monitoring (`queue/monitoring.py`)

Prometheus-compatible metrics:

| Metric | Type | Labels | Description |
|---|---|---|---|
| `celery_queue_depth` | Gauge | `queue_name` | Current tasks in queue |
| `celery_task_total` | Counter | `task_name`, `status` | Total tasks processed |
| `celery_task_failures_total` | Counter | `task_name` | Total task failures |
| `celery_task_duration_seconds` | Histogram | `task_name` | Execution time (buckets: 0.1s–300s) |

`update_queue_depths(redis_client)` refreshes all queue depth gauges from Redis.

### Beat Schedules (`queue/beat_schedules.py`)

| Schedule | Task | Interval |
|---|---|---|
| `health-check-scrapers` | `src.queue.tasks.health_check_scrapers` | Every 5 minutes |
| `data-retention-purge` | `src.queue.tasks.data_retention_purge` | Daily at 02:00 |

---

## Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (for Redis)

### 1. Start Redis

```bash
# From the repository root
docker compose up redis -d
```

This starts Redis 7 Alpine with:
- AOF persistence enabled
- `maxmemory 512mb` / `allkeys-lru` eviction
- Health check via `redis-cli ping`

### 2. Install Dependencies

```bash
cd backend
uv pip install --system -e ".[dev]"
```

### 3. Configure Environment

Copy the template and adjust as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PASSWORD` | (empty) | Redis password |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery result store |

### 4. Start a Celery Worker

```bash
celery -A backend.src.core.celery_app worker --loglevel=info
```

### 5. Start Celery Beat (scheduler)

```bash
celery -A backend.src.core.celery_app beat --loglevel=info
```

---

## Testing

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures, marker registration
├── unit/                    # Fast, no external services
│   ├── conftest.py          # Eager Celery app, fakeredis fixtures
│   ├── test_config.py       # RedisSettings, CelerySettings
│   ├── test_retry.py        # Exponential backoff logic
│   ├── test_base_task.py    # BaseScraperTask lifecycle hooks
│   ├── test_dlq.py          # DLQManager with fakeredis
│   ├── test_health.py       # Health checks with mocks
│   └── test_monitoring.py   # Prometheus metrics
└── integration/             # Requires running Redis
    ├── conftest.py          # Real Redis connection, auto-skip if unavailable
    ├── test_celery_worker.py
    ├── test_retry_real.py
    ├── test_dlq_real.py
    ├── test_health_redis.py
    └── test_beat_schedule.py
```

### Running Tests

```bash
cd backend

# Unit tests only (no Docker required)
python -m pytest tests/unit/ -m unit -v

# Integration tests (requires Redis)
docker compose up redis -d
python -m pytest tests/integration/ -m integration -v

# Full suite with coverage report
python -m pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing -v
```

Integration tests **skip gracefully** if Redis is not available — they won't fail your local run.

### Coverage

- **Current coverage:** 77% (exceeds the 60% threshold)
- HTML report: `backend/htmlcov/index.html`
- XML report: `backend/coverage.xml` (consumed by SonarCloud)
- Threshold enforced in CI and in `pyproject.toml` (`fail_under = 60`)

### What Is Tested

| Module | Unit Tests | Integration Tests | Coverage |
|---|---|---|---|
| `config.py` | Defaults, env loading, URL construction, json-only enforcement | — | 100% |
| `retry.py` | All delay values, clamping, spec compliance | — | 100% |
| `base_task.py` | Execution, max_retries, acks_late, retry_with_backoff, hooks | Worker execution, retry against Redis | 92% |
| `dlq.py` | send, list, get, paginate, purge, replay, count | send/retrieve, purge, ordering against Redis | 95% |
| `health.py` | Healthy/unhealthy mocks, queue depths | Live Redis health check, queue depths | 83% |
| `monitoring.py` | Metric existence, increment, observe, update_queue_depths | — | 100% |
| `beat_schedules.py` | — | Schedule existence, intervals, crontab type, queue options | 100% |

### Test Fixtures

- **`fake_redis`** (unit) — In-memory Redis mock via `fakeredis`. No network, no Docker.
- **`celery_app`** (unit) — Celery in `task_always_eager` mode. Tasks execute synchronously.
- **`redis_client`** (integration) — Real Redis connection. Auto-skips if Redis is down. Flushes DB on teardown.

---

## CI Pipeline

The `test-coverage` job in `.github/workflows/ci-quality.yml`:

1. Spins up a Redis 7 service container with health check
2. Installs backend dependencies with `uv`
3. Runs the full test suite with coverage
4. Uploads `coverage.xml` and `htmlcov/` as artifacts (30-day retention)

This runs in parallel with the existing Ruff, Bandit, and Safety jobs.

---

## Security Considerations

- **JSON-only serialization** — Pickle is never used (prevents arbitrary code execution, Bandit B301)
- **No hardcoded secrets** — All credentials loaded from environment variables via Pydantic Settings
- **No eval/exec** — Task deserialization is JSON-only
- **DLQ stores exception messages only** — Full tracebacks are omitted because they may contain PII from search queries (LGPD compliance)
- **Redis AOF persistence** — Queue state survives Redis restarts, critical for evidence chain of custody (CPP Art. 158-B)
- **Audit logging** — Every task start, completion, retry, and failure is logged with structured fields (task_name, task_id, timestamp)
