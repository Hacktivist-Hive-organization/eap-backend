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
 - Watch the Postgres container tutorial https://www.youtube.com/watch?v=Hs9Fh1fr5s8 since the following steps will be partially based on it.
 - Create a Docker network:   docker network create first-internship-net
 - Run a Postgres container off the official Postgres image and use the network you just created in the previous step:
      docker run --name another-postgres --network first-internship-net -e POSTGRES_PASSWORD=12345 -p 5431:5432 -d postgres
 - Connect pgAdmin to the postgres server as done in the tutorial.
 - Configure environment variables (Create a .env file (example)):
     DATABASE_TYPE=postgresql
     DATABASE_HOST=another-postgres (Docker containers can communicate by using each other's names if they both run on the same Docker network)
     DATABASE_PORT=5432
     DATABASE_USER=postgres
     DATABASE_PASSWORD=12345
     DATABASE_SCHEMA=eap
     JWT_SECRET_KEY="i am a key"
 - docker build -t eap_backend_new .   
 - docker run --name another-eap-backend --network first-internship-net -it -p 8000:8000 eap_backend_new

Note - in .env file we also have  DATABASE_NAME=eap_new, but the DB name itself does not matter. We can use the default DB name that's automatically generated when running
the Postgres container ("postgres"), or we can choose our own name in the app. It doen't matter because our app checks
if a DB by the name we provide exists, and if not, it creates it. CLARIFICATION - This is just the DB itself, one of
many potential databases inside the Postgres server. The connection info to the Postgres server has to match exactly.  



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