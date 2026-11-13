import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Brak zmiennej {name} w .env")
    return value


DB_HOST = _require('PGHOST')
DB_PORT = str(_require('PGPORT'))
DB_USER = _require('PGUSER')
DB_PASSWORD = _require('PGPASSWORD')
DB_SSL = _require('PGSSLMODE')


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)