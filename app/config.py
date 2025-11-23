from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_context: str = "/context"


settings = Settings()
