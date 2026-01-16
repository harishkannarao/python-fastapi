from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_context: str = "/context"
    app_open_api_url: str = "/openapi.json"
    app_json_logs: bool = True
    # db settings start
    app_db_migration_enabled: bool = True
    app_db_migration_mode: str = "apply"
    app_db_enabled: bool = True
    app_db_host: str = "localhost"
    app_db_port: str = "5432"
    app_db_database: str = "myuser"
    app_db_user: str = "myuser"
    app_db_password: str = "superpassword"
    app_db_min_con: int = 5
    app_db_max_con: int = 20
    app_db_log_sql: bool = False
    # db settings end


settings = Settings()
