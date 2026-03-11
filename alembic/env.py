from __future__ import with_statement
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

import sys
import os

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
sys.path.insert(0, folder)

from core.base_class import Base

target_metadata = Base.metadata

load_dotenv()


def get_url():
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "sqlite":
        db_path = os.getenv("DB_PATH", "app.db")
        return f"sqlite:///{db_path}"
    elif db_type == "mysql":
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        server = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        db = os.getenv("DB_DATABASE", "statuscode_tool")
        return f"mysql+pymysql://{user}:{password}@{server}:{port}/{db}"
    else:  # postgresql (default)
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        server = os.getenv("DB_HOST", "postgres")
        db = os.getenv("DB_DATABASE", "statuscode_tool")
        return f"postgresql://{user}:{password}@{server}/{db}"


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        is_sqlite=os.getenv("DB_TYPE", "sqlite").lower() == "sqlite",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            is_sqlite=os.getenv("DB_TYPE", "sqlite").lower() == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
