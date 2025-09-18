from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

# --- THIS IS THE FINAL, GUARANTEED FIX ---
# Add the backend folder to the Python path
sys.path.append(os.getcwd())

# Import your app's main settings and the Base for your models
from app.config import settings
from app.models import Base

# This is Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- NEW PART ---
# Set the sqlalchemy.url option in the config object dynamically
# This reads the DATABASE_URL from your Render environment variables via your Settings object
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
# --- END NEW PART ---


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Create an async engine from your app's settings
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # This mode is not typically used with async, but we keep it for completeness
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())