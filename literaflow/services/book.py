import pathlib
import uuid
from collections.abc import Iterable

import aiohttp
import asyncpg
import pydantic
import sqlalchemy as sa

import literaflow.services.exceptions as s_exceptions
from literaflow.core import config, dto, logger
from literaflow.core.db import async_session_maker
from literaflow.models import book as book_models
from literaflow.utils import files as files_utils


class BookService:
    """Service class for Book operations."""

    @staticmethod
    def _generate_destination_path(url: pydantic.HttpUrl) -> str | None:
        """Generate the destination path for the book file."""
        if not url:
            return None

        destination_path_str = f"{config.app_settings.get_books_dir_path()}/{
            uuid.uuid4()
        }.{url.path.split(".")[-1]}"

        destination_path = pathlib.Path(destination_path_str)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        return destination_path_str

    @staticmethod
    async def _download_file(
        file_to_download_url: pydantic.HttpUrl, destination_path: str
    ) -> None:
        try:
            await files_utils.download_file(
                file_to_download_url=file_to_download_url,
                destination_path=destination_path,
            )
        except TimeoutError as exc:
            raise s_exceptions.BookDownloadTimeoutError from exc
        except aiohttp.ClientError as exc:
            logger.error(
                f"Client error occurred while downloading {file_to_download_url}: {exc}"
            )
            raise s_exceptions.BookDownloadError(
                "Client error occurred while downloading the book"
            ) from exc
        except aiohttp.client_exceptions.ClientConnectorDNSError as exc:
            logger.error(
                f"Failed to resolve the DNS for the download URL: {file_to_download_url}"
            )
            raise s_exceptions.BookDownloadError(
                "Failed to resolve the DNS for the download URL"
            ) from exc
        except Exception as exc:
            logger.error(
                f"An error occurred while downloading {file_to_download_url}: {exc}"
            )
            raise s_exceptions.BookDownloadError from exc

    @classmethod
    async def create_book(cls, book_dto: dto.Book) -> book_models.Book:
        """Create a book and download its file if a URL is provided."""
        destination_path = cls._generate_destination_path(url=book_dto.url)

        if book_dto.url is not None:
            file_to_download_url = str(book_dto.url)

            await cls._download_file(
                file_to_download_url=file_to_download_url,
                destination_path=destination_path,
            )

        async with async_session_maker() as session:
            book = book_models.Book(
                name=book_dto.name,
                author=book_dto.author,
                date_published=book_dto.date_published,
                genre=book_dto.genre,
                is_denied=book_dto.is_denied,
                file_path=destination_path,
            )
            session.add(book)
            try:
                await session.commit()
            except (
                asyncpg.exceptions.UniqueViolationError,
                sa.exc.IntegrityError,
            ) as exc:
                raise s_exceptions.BookAlreadyExistsError(
                    "The book already exists in the database."
                ) from exc

            await session.refresh(book)
            return book

    @staticmethod
    async def get_books(
        filters_dto: dto.BookFilters,
    ) -> Iterable[book_models.Book]:
        """Retrieve books based on filters."""
        async with async_session_maker() as session:
            query = sa.select(book_models.Book)

            if not filters_dto.filters_exist():
                result = await session.execute(query)
                return result.scalars().all()

            if filters_dto.name:
                query = query.where(book_models.Book.name == filters_dto.name)
            if filters_dto.author:
                query = query.where(book_models.Book.author == filters_dto.author)
            if filters_dto.date_published:
                query = query.where(
                    book_models.Book.date_published == filters_dto.date_published
                )
            if filters_dto.genre:
                query = query.where(book_models.Book.genre == filters_dto.genre)

            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_book_by_id(book_id: dto.BookID) -> book_models.Book | None:
        """Retrieve a book by its ID."""
        async with async_session_maker() as session:
            result = await session.execute(
                sa.select(book_models.Book).where(book_models.Book.id == book_id)
            )
            return result.scalar_one_or_none()
