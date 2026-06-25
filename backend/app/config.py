from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "NOVELHUB_"}

    database_url: str = "sqlite+aiosqlite:///./novelhub.db"
    debug: bool = False
