from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "http://127.0.0.1:11434"
    chat_model: str = "local-agent"
    embed_model: str = "embeddinggemma"
    chroma_path: str = ""  # empty = default under data/chroma
    config_dir: str = ""
    data_dir: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def root(self) -> Path:
        return project_root()

    @property
    def config_path(self) -> Path:
        return Path(self.config_dir) if self.config_dir else self.root / "config"

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir) if self.data_dir else self.root / "data"

    @property
    def chroma_dir(self) -> Path:
        if self.chroma_path:
            return Path(self.chroma_path)
        return self.data_path / "chroma"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
