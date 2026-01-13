# ADR-002: ORM and Database Access Patterns


## Status
Accepted

## Date
2026-01-13

## Context

Uncontrolled database access leads to tightly coupled code, duplicated logic,
and poor maintainability. A consistent access pattern is required to ensure
clarity, testability, and separation of concerns.

## Decision

### Layered Architecture

Database access follows a strict layered structure:
API → Service → Repository → Database
- API layer handles HTTP concerns only
- Service layer contains business logic
- Repository layer encapsulates database access
- Database layer manages connections and sessions

### Repository Pattern

- All database queries live in repository classes
- Repositories receive a SQLAlchemy `Session`
- Repositories do not contain business logic

### Service Pattern

- Services coordinate business rules
- Services call one or more repositories
- Services do not perform direct database queries

### Session Management

- SQLAlchemy sessions are injected using FastAPI dependencies
- Sessions are never created manually

## Consequences

### Positive

- Clear separation of responsibilities
- Easier testing and refactoring
- Reduced coupling between layers

### Negative

- Slightly more boilerplate code
- Requires discipline to follow patterns

## Notes

These patterns apply to all database interactions.
Exceptions must be documented with a dedicated ADR.