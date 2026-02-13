# ADR-001: Database Schema and Migration Strategy

## Status
Accepted

## Date
2026-01-13

## Context
- The backend service requires a reliable relational database to persist
application data.
- The backend is built with FastAPI and SQLAlchemy and must support
independent backend development and long-term maintainability.

## Decision

### Database Choice
- **PostgreSQL** is the only supported relational database.
- The application uses SQLAlchemy with connection pooling.

### Schema Definition

- Database tables are defined explicitly using SQLAlchemy ORM models.
- All models inherit from a shared declarative base.

### Schema Versioning

- **Alembic** is used to manage schema migrations.
- Alembic migrations are the **single source of truth** for schema changes.
- Automatic table creation (`create_all`) is not used in production.

### Configuration

- Database connection settings are provided via environment variables.
- Alembic dynamically loads the database URL from application settings.

## Consequences

### Positive

- Schema changes are traceable and auditable
- Safe upgrades and downgrades are possible
- Environments remain consistent
- Onboarding new developers is easier

### Negative

- Additional tooling complexity
- Developers must follow migration workflows

## Notes

- Alembic must be used for all schema changes.
- Manual schema modifications are not permitted.