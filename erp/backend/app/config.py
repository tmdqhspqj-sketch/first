import os

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ERP_", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    admin_login: str = "admin"
    admin_password: str = "admin"
    hong_login: str = "hongseungbo"
    hong_password: str = "hongsb"
    database_url: str = "sqlite:///./erp.db"
    token_expire_hours: int = 12
    cors_origins: str = (
        "http://localhost:3001,http://127.0.0.1:3001,http://localhost:3000,"
        "https://first-erp-pearl.vercel.app"
    )
    purge_interval_hours: int = 6
    deactivate_purge_days: int = 7

    @model_validator(mode="after")
    def resolve_database_url(self) -> "Settings":
        if self.database_url == "sqlite:///./erp.db":
            for key in ("ERP_DATABASE_URL", "POSTGRES_URL", "DATABASE_URL"):
                value = os.environ.get(key)
                if value:
                    object.__setattr__(self, "database_url", value)
                    break
        return self


settings = Settings()
