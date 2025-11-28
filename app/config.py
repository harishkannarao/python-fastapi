from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_context: str = "/context"
    app_open_api_url: str = "/openapi.json"
    app_json_logs: bool = True


settings = Settings()
