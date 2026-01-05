from databases import Database
from sqlmodel import Session, create_engine

from app.config import settings

DATABASE_URL = f"postgresql://{settings.app_db_user}:{settings.app_db_password}@{settings.app_db_host}:{settings.app_db_port}/{settings.app_db_database}"
database = Database(
    DATABASE_URL, min_size=settings.app_db_min_con, max_size=settings.app_db_max_con
)
engine = create_engine(
    DATABASE_URL,
    pool_size=settings.app_db_min_con,
    max_overflow=settings.app_db_max_con - settings.app_db_min_con,
    echo=True,
)


def get_session():
    with Session(engine) as session:
        yield session
