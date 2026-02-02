# Database Migrations with Alembic
We use Alembic to manage database schema changes in a versioned and reproducible way.

# Install Alembic
    pip install alembic

# Initialize Alembic (once per project)
    alembic init alembic
- Creates the alembic/ folder with configuration (alembic.ini) and env.py
- Do not run again after the initial setup

# Create a migration
    alembic revision --autogenerate -m "your message here"
Alembic will compare your models to the database and generate a migration script in alembic/versions/
example: alembic revision --autogenerate -m "initial schema"

# Apply migrations
    alembic upgrade head
- Creates or updates tables in the database
- Now we don't use Base.metadata.create_all() in production(main.py) — Alembic handles schema

#  Downgrade migrations
- Revert the last migration:
  - alembic downgrade -1
-Revert to a specific migration:
  - alembic downgrade <revision_hash>
-Revert all migrations (drop all tables):
  - alembic downgrade base

# View migration history
    alembic history --verbose

# View current migration
    alembic current


# First-time setup
1. Ensure the database exists (e.g., `eap`) and the user has privileges.
2. Run the initial migration:
   alembic revision --autogenerate -m "initial schema"
   alembic upgrade head
