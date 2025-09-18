import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import os
import sys

sys.path.append(os.getcwd())

from app.config import settings
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    # This part is not used in production, but we keep it
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())