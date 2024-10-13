import sqlalchemy.ext.asyncio as sa_asyncio_ext

import sqlalchemy.orm as sa_orm

from literaflow.core.config import postgresql_connection_settings

async_engine: sa_asyncio_ext.AsyncEngine = sa_asyncio_ext.create_async_engine(
    postgresql_connection_settings.async_url,
    echo=postgresql_connection_settings.IS_ECHO,
)
async_session_maker: sa_asyncio_ext.async_sessionmaker = (
    sa_asyncio_ext.async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
    )
)


class Base(sa_orm.DeclarativeBase):
    pass


async def create_tables() -> None:
    """Create database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
