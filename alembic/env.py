# alembic/env.py

from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from sqlalchemy import pool
from logging.config import fileConfig
from app.db.database import Base
from app.db.schemas import *
from app.configuration.config import settings
from alembic import context
import asyncio


# Get the configuration from alembic.ini
config = context.config

# Ensure the logging configuration is set up
fileConfig(config.config_file_name)

# Set the target metadata for Alembic to work with
target_metadata = Base.metadata

def get_url():
    """Fetches the database URL dynamically from settings."""
    return settings.DATABASE_URL

# Add your custom logic to fetch the database URL if you need
config.set_main_option("sqlalchemy.url", get_url())

# Function to get the asynchronous engine
def get_async_engine():
    database_url = config.get_main_option("sqlalchemy.url")
    engine = create_async_engine(database_url, echo=True, future=True)
    return engine

def do_run_migrations(connection):
    """Run migrations using a synchronous connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use async_engine_from_config for async migrations
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        
        await connectable.dispose()

    import asyncio
    asyncio.run(do_run_async_migrations())

# Main entry point to start the migrations
if context.is_offline_mode():
    print("Offline mode is not supported for async migrations.")
else:
    # Run the migrations in an async event loop
    run_migrations_online()
