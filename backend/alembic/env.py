import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import os
import sys

# --- THIS IS THE FINAL, GUARANTEED FIX ---
# Add the parent directory to the Python path so this script can find the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your app's main settings object and the Base for your models
from app.config import settings
from app.models import Base

# This is the Alembic Config object
config = context.config

# --- This is the crucial part that bypasses the .ini error ---
# We programmatically set the sqlalchemy.url option in the config object.
# This reads the DATABASE_URL from your Render environment variables via your app's Settings object.
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
# --- End of crucial part ---


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

# --- ASYNC MIGRATION CONFIGURATION ---
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    # This part is not used in production, but we keep it for completeness
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())