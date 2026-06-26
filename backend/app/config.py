from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "NOVELHUB_"}

    database_url: str = "sqlite+aiosqlite:///./novelhub.db"
    debug: bool = False

    llm_provider: str = "local"
    llm_base_url: str = "http://127.0.0.1:10124"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_timeout: float = 120.0
