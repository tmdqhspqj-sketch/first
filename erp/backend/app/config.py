from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    super_login: str = "hongseungbo"
    super_password: str = "hongsb"
    database_url: str = "sqlite:///./erp.db"
    token_expire_hours: int = 12
    cors_origins: str = "http://localhost:3001,http://127.0.0.1:3001,http://localhost:3000"


settings = Settings()
