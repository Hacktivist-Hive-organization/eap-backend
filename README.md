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
   - Windows (Command Prompt): .venv\Scripts\activate.bat
   - Windows (PowerShell): .venv\Scripts\Activate.ps1
   - macOS / Linux (Terminal, bash/zsh): source .venv/bin/activate
 - install dependencies (pip install -r requirements.txt)
   - Configure environment variables (Create a .env file (example)):
       - DATABASE_TYPE=postgresql  
       - DATABASE_HOST=127.0.0.1  
       - DATABASE_PORT=5432  
       - DATABASE_USER=user1  
       - DATABASE_PASSWORD=user123  
       - DATABASE_NAME=eap  
 - Create the PostgreSQL database
 - run the project (uvicorn app.main:app --reload)
 - Check the health endpoint

## Alternative setups

For alternative setups, refer to the "deployment options" directory. 

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