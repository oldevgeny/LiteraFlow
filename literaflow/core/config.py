import pathlib

import sqlalchemy.engine.url as sa_url
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings."""

    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 8000

    BOOKS_DIR: str = "books"

    def get_books_dir_path(self) -> str:
        """Get the path to the books' directory."""
        return (
            f"{pathlib.Path(__file__).resolve().parent.parent.parent}/{self.BOOKS_DIR}"
        )


class PostgreSQLConnectionSettings(BaseSettings):
    """PostgreSQL connection settings."""

    DB_NAME: SecretStr
    DB_HOST: SecretStr
    DB_PORT: SecretStr
    DB_USER: SecretStr
    DB_PASS: SecretStr

    IS_ECHO: bool = False

    @property
    def async_url(self) -> sa_url.URL:
        """Create an async URL for the PostgreSQL connection."""
        return sa_url.URL.create(
            drivername="postgresql+asyncpg",
            database=self.DB_NAME.get_secret_value(),
            username=self.DB_USER.get_secret_value(),
            password=self.DB_PASS.get_secret_value(),
            host=self.DB_HOST.get_secret_value(),
            port=int(self.DB_PORT.get_secret_value()),
        )


app_settings = AppSettings()
postgresql_connection_settings = PostgreSQLConnectionSettings()
