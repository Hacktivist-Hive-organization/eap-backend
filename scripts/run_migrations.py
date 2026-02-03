import sys

from alembic import command
from alembic.config import Config

alembic_cfg = Config("alembic.ini")
## this script is to be run from dokker before starting up the application server (uvicorn)
# so the Alembic migration applied first
try:
    command.upgrade(alembic_cfg, "head")
    print("Alembic migrations applied successfully!")
except Exception as e:
    print(f" Migration failed: {e}")
    sys.exit(1)
