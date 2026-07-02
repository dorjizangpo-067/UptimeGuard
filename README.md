# UptimeGuard

A **production-grade**, asynchronous personal service and API monitoring tool built with FastAPI and Celery. UptimeGuard tracks the availability and latency of your applications in the background and sends immediate notifications if any service goes down.

---

## 🚀 Planned Features

- **Asynchronous Health Checks:** High-frequency service pings powered by `httpx` without blocking the API.
- **Background Scheduling:** Automated periodic checks managed via Celery Beat.
- **Secure Dashboard API:** *Implemented* JWT-based user authentication and secure CRUD endpoints for managing users (signup, update). CRUD for monitored URLs is planned.
- **Real-Time Alerts:** Automated email notifications via `fastapi-mail` triggered immediately upon service failure.
- **Performance Metrics:** Historic latency tracking and uptime percentage calculations.

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance async web framework |
| **Package Manager**| `uv` | Ultra-fast Python dependency management |
| **Database & ORM** | PostgreSQL + SQlalchemy | Async database operations with Pydantic alignment |
| **Migrations** | Alembic | Database schema evolution tracking |
| **Task Queue** | Celery + Redis | Background task worker and message broker |
| **HTTP Client** | HTTPX | Non-blocking async requests for target pinging |
| **Code Editor** | Neovim | I prefer Terminal workflow, so I use neovim |
| **Version Control** | Git | I use git for code version control, and Lazygit made my workflow fast and easy |

---

## 📐 High-Level Architecture

```text
[ User / Frontend ] ──(JWT Auth)──> [ FastAPI App ] <───> [ PostgreSQL ]
                                         │                      ▲
                                   (Push Tasks)                 │
                                         ▼                 (Log Results)
[ Celery Beat (Scheduler) ] ───> [ Redis Broker ] <───> [ Celery Workers ]
                                                                │
                                                           (Ping Targets /
                                                            Send Emails)
