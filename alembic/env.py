# alembic/env.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from sqlalchemy import pool, MetaData
from logging.config import fileConfig
from alembic import context

from app.db.database import Base
from app.configuration.config import settings

from app.db.models.user_model import User
from app.db.models.session_model import UserSession
from app.db.models.otp_model import OTP
from app.db.models.phone_number import PhoneNumber
from app.db.models.address_model import Address
from app.db.models.log_model import Log
from app.db.models.image_model import Image
from app.db.models.detection_model import Detection
from app.db.models.processed_image_model import ProcessedImage
from app.db.models.subscription import Features, FeatureGroup, SubscriptionPlan
from app.db.models.order_model import Order
from app.db.models.user_activity_model import ActiveUserPlans, UserActivity


# Get the configuration from alembic.ini
config = context.config

# Ensure the logging configuration is set up
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create a metadata object with naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Import all models explicitly
# This ensures all models are loaded and their tables are registered
all_models = [
    User, UserSession, OTP, PhoneNumber, Address, 
    Log, Image, Detection, ProcessedImage,
    Features, FeatureGroup, SubscriptionPlan,
    Order, ActiveUserPlans, UserActivity
]

# Set the target metadata for Alembic to work with
target_metadata = Base.metadata

def get_url():
    """Fetches the database URL dynamically from settings."""
    return settings.DATABASE_URL

# Add your custom logic to fetch the database URL if you need
config.set_main_option("sqlalchemy.url", get_url())

def do_run_migrations(connection):
    """Run migrations using a synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Compare column types
        compare_server_default=True,  # Compare server defaults
        include_schemas=True,  # Include schema names
        render_as_batch=True,  # Enable batch mode for SQLite compatibility
        user_module_prefix=None,  # Don't prefix table names
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use async_engine_from_config for async migrations
    configuration = config.get_section(config.config_ini_section)
    url = configuration["sqlalchemy.url"]
    connectable = create_async_engine(url, 
        echo=True,
        future=True,
        pool_pre_ping=True
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()

# Main entry point to start the migrations
if context.is_offline_mode():
    print("Offline mode is not supported for async migrations.")
else:
    # Run the migrations in an async event loop
    asyncio.run(run_migrations_online())