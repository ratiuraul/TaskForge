# SaaS Project Management Platform

> A production-style Project Management Platform built with FastAPI, following Clean Architecture, Domain-Driven Design principles, and modern backend engineering practices.

---

## Features

- JWT Authentication
- Refresh Tokens
- Google OAuth
- Email Verification
- Password Reset

- Organizations

- Teams

- Projects

- Kanban Boards

- Tasks

- Comments

- Attachments

- Notifications

- Activity Logs

- Dashboard

- Full Text Search

- RBAC

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic
- Pydantic v2

### Infrastructure

- Docker
- Docker Compose
- Nginx

### Background

- Redis
- Celery

### Storage

- MinIO (development)
- AWS S3 compatible

### Testing

- pytest
- httpx
- pytest-asyncio

### Quality

- Ruff
- Black
- mypy
- pre-commit

### CI/CD

- GitHub Actions

---

## Architecture

(Add architecture diagram)

---

## Folder Structure

(Add folder structure)

---

## Installation

```bash
git clone ...

docker compose up
```

---

## Running Migrations

```bash
alembic upgrade head
```

---

## Running Tests

```bash
pytest
```

---

## Documentation

docs/

Architecture

Database

API

Deployment

---

## Roadmap

- [x] Authentication
- [ ] Organizations
- [ ] Teams
- [ ] Projects
- [ ] Boards
- [ ] Tasks
- [ ] Notifications

---

## License

MIT
