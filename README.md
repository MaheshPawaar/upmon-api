# upmon-api

A self-hosted uptime monitoring API. Register URLs, get them pinged on a schedule, track downtime incidents, and receive alerts — all through a clean REST API.

**Stack:** FastAPI · PostgreSQL · Redis · Celery · Docker

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                               │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP REST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI (port 8000)                      │
│  /auth    /monitors    /checks    /stats    /incidents      │
└──────┬──────────────────────────┬───────────────────────────┘
       │                          │
       ▼                          ▼
┌─────────────┐          ┌────────────────┐
│  PostgreSQL │          │     Redis      │
│  users      │          │  stats cache   │
│  monitors   │          │  task broker   │
│  checks     │          └───────┬────────┘
│  incidents  │                  │
└──────▲──────┘         ┌────────┴────────┐
       │                ▼                 ▼
       │     ┌─────────────────┐  ┌───────────────┐
       │     │  CELERY BEAT    │  │ CELERY WORKER │
       │     │ dispatch_checks │─▶│ health_check  │
       │     │ every 60s       │  │ send_alert    │
       │     └─────────────────┘  └──────┬────────┘
       │                                 │ httpx GET
       └─────────────────────────────────┤
                    Write Results        ▼
                               ┌─────────────────┐
                               │  MONITORED URLs │
                               └─────────────────┘
```

---

## API Endpoints

| Method | Endpoint                           | Auth | Description                     |
| ------ | ---------------------------------- | ---- | ------------------------------- |
| POST   | `/api/auth/register`               | No   | Register a new user             |
| POST   | `/api/auth/login`                  | No   | Login, returns JWT              |
| POST   | `/api/monitors`                    | Yes  | Create a monitor                |
| GET    | `/api/monitors`                    | Yes  | List your monitors              |
| GET    | `/api/monitors/{id}`               | Yes  | Get a monitor                   |
| PATCH  | `/api/monitors/{id}`               | Yes  | Update a monitor                |
| DELETE | `/api/monitors/{id}`               | Yes  | Delete a monitor                |
| GET    | `/api/monitors/{id}/checks`        | Yes  | Paginated check history         |
| GET    | `/api/monitors/{id}/checks/latest` | Yes  | Last 10 checks                  |
| GET    | `/api/monitors/{id}/stats`         | Yes  | Uptime %, response times, p95   |
| GET    | `/api/monitors/{id}/incidents`     | Yes  | All incidents (open + resolved) |

---

## How to Run

```bash
cp .env.example .env   # fill in SECRET_KEY
docker-compose up --build
```

API available at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`.

---

## Design Decisions

**Dispatcher pattern over per-monitor beat entries**
A single `dispatch_checks()` task fires every 60s and queries which monitors are due, then fans out individual tasks. Adding a Celery Beat entry per monitor doesn't scale — the dispatcher keeps the schedule dynamic without touching Beat config.

**Redis stats caching**
Stats queries (uptime %, p95 response time) hit multiple rows across large time windows. Results are cached at `stats:{monitor_id}` with a 60s TTL and invalidated on every new check result write.

**Incident state machine**
Health checks drive a four-case state machine: down + no open incident → create incident + alert; up + open incident → resolve it; otherwise → do nothing. This prevents duplicate alerts and tracks resolution time cleanly.
