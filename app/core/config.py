from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    ENV: Optional[str] = None
    RELEASE: Optional[str] = None

    API_V1_STR: str = "/api/api_v1"
    PROJECT_NAME: str = "statuscode_test_tool"

    SENTRY_DSN: Optional[str] = None

    # Database Configuration
    DB_TYPE: str = "sqlite"  # sqlite, mysql, postgresql
    DB_HOST: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_DATABASE: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_PATH: str = "app.db"  # For SQLite
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # TEST DATABASE
    TEST_DB_TYPE: str = "sqlite"
    TEST_DB_HOST: str = "localhost"
    TEST_DB_USER: Optional[str] = None
    TEST_DB_PASSWORD: str = ""
    TEST_DB_PORT: Optional[str] = None
    TEST_DB_DATABASE: str = "test_statuscode_tool"
    TEST_DB_PATH: str = "test_app.db"
    TEST_SQLALCHEMY_DATABASE_URI: str = ""

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, info) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        db_type = values.get("DB_TYPE", "sqlite").lower()

        if db_type == "sqlite":
            db_path = values.get("DB_PATH", "app.db")
            return f"sqlite+aiosqlite:///{db_path}"
        elif db_type == "mysql":
            user = values.get("DB_USER")
            password = values.get("DB_PASSWORD")
            host = values.get("DB_HOST", "localhost")
            port = values.get("DB_PORT", "3306")
            database = values.get("DB_DATABASE", "statuscode_tool")
            return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
        else:  # postgresql (default)
            user = values.get("DB_USER", "postgres")
            password = values.get("DB_PASSWORD", "")
            host = values.get("DB_HOST", "postgres")
            database = values.get("DB_DATABASE", "statuscode_tool")
            return f"postgresql+asyncpg://{user}:{password}@{host}/{database}"

    @field_validator("TEST_SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def _assemble_test_db_connection(cls, v: str, info) -> str:
        values = info.data
        db_type = values.get("TEST_DB_TYPE", "sqlite").lower()

        if db_type == "sqlite":
            db_path = values.get("TEST_DB_PATH", "test_app.db")
            return f"sqlite+aiosqlite:///{db_path}"
        elif db_type == "mysql":
            user = values.get("TEST_DB_USER", "root")
            password = values.get("TEST_DB_PASSWORD", "")
            host = values.get("TEST_DB_HOST", "localhost")
            port = values.get("TEST_DB_PORT", "3306")
            database = values.get("TEST_DB_DATABASE", "test_statuscode_tool")
            return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
        else:  # postgresql (default)
            user = values.get("TEST_DB_USER", "postgres")
            password = values.get("TEST_DB_PASSWORD", "")
            host = values.get("TEST_DB_HOST", "localhost")
            port = values.get("TEST_DB_PORT", "5432")
            database = values.get("TEST_DB_DATABASE", "test_statuscode_tool")
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings = Settings()
