from databases import Database
from app.config import settings

DATABASE_URL = f"postgresql://{settings.app_db_user}:{settings.app_db_password}@{settings.app_db_host}/{settings.app_db_database}"
database = Database(
    DATABASE_URL, min_size=settings.app_db_min_con, max_size=settings.app_db_max_con
)
