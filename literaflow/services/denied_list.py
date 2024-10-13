import sqlalchemy as sa

from literaflow.core.db import async_session_maker
from literaflow.models.book import Book
from literaflow.utils.denied_books_parser import DeniedBooksDict


class DeniedListService:
    """Service class for managing denied books."""

    @staticmethod
    async def update_denied_books(denied_books: DeniedBooksDict) -> None:
        """Update books to be marked as denied."""
        async with async_session_maker() as session:
            stmt = (
                sa.update(Book)
                .where(
                    sa.or_(
                        Book.name.in_(denied_books["names"]),
                        Book.author.in_(denied_books["authors"]),
                    )
                )
                .values(is_denied=True)
            )
            await session.execute(stmt)
            await session.commit()
