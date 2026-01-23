# EAP Backend API
A FastAPI-based backend providing REST APIs, using PostgreSQL as the database and SQLAlchemy as the ORM.  
Supports modular structure for routes, models, and database configuration.  
API versioning is enabled (`/api/v1/...`) and interactive docs are available via Swagger/OpenAPI.

## Features
- FastAPI application with versioned API (`/api/v1/...`)
- PostgreSQL integration with SQLAlchemy
- Modular project structure:
  - `app/api` → API routes, schemas, dependencies
  - `app/models` → Database models
  - `app/repositories` → CRUD operation
  - `app/services` → business logic
  - `app/core` → Configuration and security
  - `app/database` → database session
  - `app/common` → exception handling, enums, loggers
- Health check endpoint (`/api/routes/v1/health`) showing app and DB status
- Auto table creation (development mode)
- Optional: Alembic for database migrations (recommended for production)


## Setup
 - clone repository
 - Create a Python virtual environment .venv (python -m venv .venv)
 - activate virtual environment
 - install dependencies (pip install -r requirements.txt)
 - Install pgAdmin
 - Run a Postgres container by following the tutorial: https://www.youtube.com/watch?v=Hs9Fh1fr5s8
 - Configure environment variables (Create a .env file (example)):
     DATABASE_TYPE=postgresql
     DATABASE_HOST=127.0.0.1
     DATABASE_PORT=5431 (Or whatever port in your host, which you mapped to the Postgres container's port, as explained in the tutorial)
     DATABASE_USER=postgres (same as you used in the container)
     DATABASE_PASSWORD=12345 (same as you used in the container)
     DATABASE_SCHEMA=eap
     JWT_SECRET_KEY="i am a key"
 - run the project (uvicorn app.main:app --reload)
 - Check the health endpoint

## Running Unit Tests

Unit tests are located in the `tests/unit/` directory and are fully isolated
from external infrastructure such as databases and external services.

### Prerequisites
- Python 3.11+
- Virtual environment activated
- Development dependencies installed

### Install dependencies
```bash
pip install -r requirements-dev.txt