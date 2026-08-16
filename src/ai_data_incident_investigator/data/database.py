from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from ai_data_incident_investigator.core.config import settings


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def test_connection() -> str:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        return result.scalar_one()