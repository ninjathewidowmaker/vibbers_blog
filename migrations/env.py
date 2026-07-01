import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context


from app.database import DATABASE_URL
from app.models import Base, Blog, Template  


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option("sqlalchemy.url", DATABASE_URL)


target_metadata = Base.metadata 


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to execute migrations inside the sync runner context."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an AsyncEngine and associate a
    connection with the context.
    """
    
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
      
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()



if context.is_offline_mode():
    run_migrations_offline()
else:
    
    asyncio.run(run_migrations_online())