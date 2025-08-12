import asyncio
import os
import pathlib
import sys
from logging.config import fileConfig

import alembic
from psycopg2 import DatabaseError
from sqlalchemy import engine_from_config, create_engine, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config


from alembic import context

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.config import POSTGRES_DB, DATABASE_URL
from app.database.db import Base

database_url = DATABASE_URL

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# 1. from myapp import mymodel
from app.models.users import User

# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    if os.environ.get("TESTING"):
        raise DatabaseError("Running testing migrations offline currently not permitted.")

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# async def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     print('\n\n', 100 * "*")
#     print('\n\n', os.environ.get("TESTING"))
#     connectable = async_engine_from_config()
#     DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else str(DATABASE_URL)
#
#     # handle testing config for migrations
#     if os.environ.get("TESTING"):
#         # connect to primary db
#         default_engine = create_engine(str(DATABASE_URL), isolation_level="AUTOCOMMIT")
#         # drop testing db if it exists and create a fresh one
#         with default_engine.connect() as default_conn:
#             default_conn.execute(f"DROP DATABASE IF EXISTS {POSTGRES_DB}_test")
#             default_conn.execute(f"CREATE DATABASE {POSTGRES_DB}_test")
#
#     connectable = async_engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )
#     config.set_main_option("sqlalchemy.url", DB_URL)
#
#     async with connectable.connect() as connection:
#         await connection.run_sync(do_run_migrations)
#     await connectable.dispose()
#
#
#     if connectable is None:
#         connectable = engine_from_config(
#             config.get_section(config.config_ini_section),
#             prefix="sqlalchemy.",
#             poolclass=pool.NullPool,
#         )
#
#     with connectable.connect() as connection:
#         alembic.context.configure(
#             connection=connection,
#             target_metadata=None
#         )
#
#         with alembic.context.begin_transaction():
#             alembic.context.run_migrations()
#
#     # previous
#     # asyncio.run(run_async_migrations())

async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    """
    DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else str(DATABASE_URL)

    # handle testing config for migrations
    if os.environ.get("TESTING"):
        # connect to primary db
        default_engine = create_engine(str(DATABASE_URL), isolation_level="AUTOCOMMIT")
        # drop testing db if it exists and create a fresh one
        with default_engine.connect() as default_conn:
            default_conn.execute(f"DROP DATABASE IF EXISTS {POSTGRES_DB}_test")
            default_conn.execute(f"CREATE DATABASE {POSTGRES_DB}_test")

    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", DB_URL)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=None
        )

        with alembic.context.begin_transaction():
            alembic.context.run_migrations()

# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#
#     asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
