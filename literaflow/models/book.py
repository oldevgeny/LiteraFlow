import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import literaflow.models.annotations as m_annotations
from literaflow.core.db import Base

metadata_obj = sa.MetaData()


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (sa.UniqueConstraint("name", "author", "date_published"),)

    id: sa_orm.Mapped[m_annotations.int_pk]
    created_at: sa_orm.Mapped[m_annotations.created_at]
    updated_at: sa_orm.Mapped[m_annotations.updated_at]

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(nullable=False)
    author: sa_orm.Mapped[str] = sa_orm.mapped_column(nullable=False)
    date_published: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(nullable=False)

    genre: sa_orm.Mapped[str] = sa_orm.mapped_column(default="")
    is_denied: sa_orm.Mapped[bool] = sa_orm.mapped_column(server_default="false")
    file_path: sa_orm.Mapped[str | None] = sa_orm.mapped_column(nullable=True)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the book."""
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "date_published": self.date_published.isoformat(),
            "genre": self.genre,
            "is_denied": self.is_denied,
            "file_path": self.file_path,
        }
