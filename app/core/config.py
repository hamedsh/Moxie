from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings and configuration.
    
    Configuration can be provided via environment variables or .env file.
    """
    
    # Environment
    ENV: Optional[str] = None
    RELEASE: Optional[str] = None

    # API Configuration
    API_V1_STR: str = "/api/api_v1"
    PROJECT_NAME: str = "statuscode_test_tool"

    # Sentry (error tracking)
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

    # Database Connection Pool Configuration
    DB_POOL_SIZE: int = 20  # Number of connections to keep in the pool
    DB_POOL_MAX_OVERFLOW: int = 10  # Maximum overflow connections beyond pool_size
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after this many seconds (1 hour)
    DB_POOL_PRE_PING: bool = True  # Test connections before using them
    DB_ECHO: bool = False  # Echo SQL statements (useful for debugging)

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
        """Assemble database connection URI from components."""
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
        """Assemble test database connection URI."""
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
