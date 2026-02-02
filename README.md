# EAP Backend API
A FastAPI-based backend providing REST APIs, using PostgreSQL as the database and SQLAlchemy as the ORM.  
Supports modular structure for routes, models, and database configuration.  
API versioning is enabled (`/api/v1/...`) and interactive docs are available via Swagger/OpenAPI.

## Features
- FastAPI application with versioned API (`/api/v1/...`)
- PostgreSQL integration with SQLAlchemy
- Modular project structure:
  - `app/api` → API routes, schemas, dependencies
  - `app/common` → exception handling, enums, loggers
  - `app/core` → Configuration and security
  - `app/database` → database session
  - `app/models` → Database models
  - `app/repositories` → CRUD operation
  - `app/services` → business logic
  
- Health check endpoint (`/api/routes/v1/health`) showing app and DB status
- Auto table creation (development mode)
- Optional: Alembic for database migrations (recommended for production)


## Setup
 - clone repository
 - Create a Python virtual environment .venv (python -m venv .venv)
 - activate virtual environment 
   - Windows (Command Prompt):
    ```bash
    .venv\Scripts\activate.bat
    ```

   - Windows (PowerShell):
    ```powershell
    .\venv\Scripts\Activate.ps1'"
    ``` 

   - macOS / Linux (Terminal, bash/zsh): source .venv/bin/activate


- install dependencies
```bash
pip install -r requirements.txt
``` 
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

## Running the app
```bash
uvicorn app.main:app
```



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
```

## Code Formatting and Pre-commit Hooks
Enforce consistent code style using **Black** and **isort**. Checks run locally before commit and in CI.

#### One-time setup
- Install development dependencies 

```bash
pip install -r requirements-dev.txt
```

- Install the pre-commit Git hook pre-commit Git hook to automatically format files before committing
```bash
pre-commit install
```

#### Local workflow
- Stage your files before committing
- Commit changes
  - If files are formatted correctly, the commit succeeds
  - If formatting issues exist, pre-commit fixes files automatically and stops the commit
  - Re-stage the fixed files and commit again

#### Manual formatting
- Run pre-commit on all files to format them manually
 ``` bash
pre-commit run --all-files
```

- Ensures consistency with rules defined in pyproject.toml and .pre-commit-config.yaml

#### CI enforcement
- On every push or pull request to dev branch Pre-commit formatting checks are run
- If formatting or tests fail, the workflow fails and the PR cannot be merged

#### Summary
- One-time: install pre-commit and Git hook

- Normal workflow: 
  - stage → commit → pre-commit auto-fixes if needed
- Optional manually: pre-commit on all files
``` bash
pre-commit run --all-files
```

- CI ensures code is formatted correctly before merge
