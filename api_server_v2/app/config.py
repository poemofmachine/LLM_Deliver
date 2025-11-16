from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Memory Hub v2"
    workspace_default: str = "default"


settings = Settings()
