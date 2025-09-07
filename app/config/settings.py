from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str

    # Security
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 60

    # Application
    app_name: str = "Expense Tracker API"
    app_version: str = "1.0.0"
    debug: bool = False

    # environment file
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
