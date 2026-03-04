from pathlib import Path
from typing import Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    ENV: str = None
    RELEASE: str = None

    API_V1_STR: str = "/api/api_v1"
    PROJECT_NAME: str = "statuscode_test_tool"

    SENTRY_DSN: str = None

    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # POSTGRESQL TEST DATABASE
    TEST_DB_HOSTNAME: str = "postgres"
    TEST_DB_USER: str = "postgres"
    TEST_DB_PASSWORD: str = ""
    TEST_DB_PORT: str = "5432"
    TEST_DB_DATABASE: str = "statuscode_tool"
    TEST_SQLALCHEMY_DATABASE_URI: str = ""

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, info) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        user = values.get("DB_USER")
        password = values.get("DB_PASSWORD")
        host = values.get("DB_HOST")
        database = values.get("DB_DATABASE") or ""
        return f"postgresql+asyncpg://{user}:{password}@{host}/{database}"

    @field_validator("TEST_SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def _assemble_test_db_connection(cls, v: str, info) -> str:
        values = info.data
        user = values["TEST_DB_USER"]
        password = values["TEST_DB_PASSWORD"]
        host = values["TEST_DB_HOSTNAME"]
        port = values["TEST_DB_PORT"]
        database = values["TEST_DB_DATABASE"]
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/test_{database}"

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings = Settings()
